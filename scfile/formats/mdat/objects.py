from uuid import UUID

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import DecodingError
from scfile.io.mdat import MdatReader


def objects(
    data: bytes,
    version: int,
) -> S.ChunkObjects:
    raw = memoryview(data)
    container = S.ChunkObjects()
    decoded: list[S.ChunkObject] = []

    with MdatReader(data) as reader:
        try:
            count = reader.varuint()
            container.count = count
            for index in range(count):
                size = reader.varuint()
                offset = reader.tell()
                end = offset + size

                decoded.append(_object(reader, raw[offset:end], index, offset, version))
                reader.seek(end)

        except DecodingError as error:
            container.error = str(error)

        if container.error is None and reader.tell() != len(raw):
            container.error = "Bytes remain after declared objects"

    container.objects = tuple(decoded)
    return container


def _header(reader: MdatReader, version: int) -> S.ObjectHeader:
    match version:
        case 6:
            network_id = reader.value(F.U16)
        case _:
            network_id = reader.value(F.U64)

    flags, flags2 = reader.unpack(f"{F.U32}{F.U8}")

    group = None
    if flags & 0x80:
        group = UUID(bytes=reader.read_exact(16))
        reader.skip(16)
        children = reader.value(F.I32)
        if children < 0:
            raise DecodingError("Negative children count")
        reader.skip(children * 16)
        reader.java_utf()
        reader.skip(1 + 1 + 4)

    if flags & 0x8000:
        reader.skip(reader.value(F.U16))
    if flags & 0x4000:
        reader.skip(4)
    if flags & 0x2000:
        reader.skip(4)
    if flags & 0x400:
        reader.skip(4)
    if version == 6:
        reader.skip(4)

    return S.ObjectHeader(network_id, flags, flags2, group)


def _object(reader: MdatReader, raw: memoryview, index: int, offset: int, version: int) -> S.ChunkObject:
    obj = S.ChunkObject(index, offset, raw=raw)

    try:
        header = _header(reader, version)
        obj.header = header

        uuid = UUID(bytes=reader.read_exact(16))
        matrix = (reader.vector3(), reader.vector3(), reader.vector3())
        position = reader.vector3()
        obj.placement = S.ObjectPlacement(uuid, matrix, position)

        flags, flags2 = header.flags, header.flags2
        activation = reader.value(F.I8)
        feature_flag = None
        if flags & 0x1000:
            feature_flag = reader.java_utf()

        collision_render = None
        if flags & 0x800:
            collision_render = reader.value(F.I8)

        collision_status = reader.value(F.I8)
        render_model_selection = reader.value(F.U8)
        custom_behaviour = None
        if flags & 0x200:
            custom_behaviour = reader.java_utf()

        obj.settings = S.ObjectSettings(
            active=bool(flags2 & 4),
            activation=activation,
            feature_flag=feature_flag,
            render_collision_status=collision_render,
            collision_status=collision_status,
            render_model_selection=render_model_selection,
            custom_behaviour=custom_behaviour,
        )

    except (DecodingError, UnicodeError) as error:
        obj.error = str(error)

    return obj


