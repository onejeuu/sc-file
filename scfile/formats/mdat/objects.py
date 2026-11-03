from uuid import UUID

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.mdat import MdatReader


def _header(reader: MdatReader, version: int) -> S.ObjectHeader:
    match version:
        case 6:
            type_id = reader.value(F.U16)
        case 7:
            type_id = reader.value(F.U64)
        case _:
            raise DecodingError(
                f"Unsupported MDAT object version: {version}.",
                location=reader.location,
                offset=reader.tell(),
            )

    flags, flags2 = reader.unpack(f"{F.U32}{F.U8}")
    if flags & ~0x3FBFF or flags2 & ~7:
        raise DecodingError(
            "Unknown object flags; header boundary unavailable",
            location=reader.location,
            offset=reader.tell(),
        )

    group = None
    if flags & 0x80:
        group = UUID(bytes=reader.read_exact(16))

    if flags & 0x8000:
        reader.java_utf()
    if flags & 0x4000:
        reader.value(F.I32)
    if flags & 0x2000:
        reader.value(F.I32)
    if version == 6:
        reader.value(F.I32)

    return S.ObjectHeader(type_id, flags, flags2, group)


def _object(reader: MdatReader, raw: memoryview, index: int, offset: int, end: int, version: int) -> S.ChunkObject:
    item = S.ChunkObject(index, offset, raw)

    try:
        header = _header(reader, version)
        item.header = header

        uuid = UUID(bytes=reader.read_exact(16))
        matrix = (reader.vector3(), reader.vector3(), reader.vector3())
        position = reader.vector3()
        item.placement = S.ObjectPlacement(uuid, matrix, position)

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

        item.settings = S.ObjectSettings(
            active=bool(flags2 & 4),
            activation=activation,
            feature_flag=feature_flag,
            render_collision_status=collision_render,
            collision_status=collision_status,
            render_model_selection=render_model_selection,
            custom_behaviour=custom_behaviour,
        )
        if reader.tell() > end:
            raise BinaryStructureError(location=reader.location, offset=end)

    except (DecodingError, UnicodeError) as error:
        item.error = str(error)

    return item


def objects(data: bytes, version: int) -> S.ChunkObjects:
    if version not in (6, 7):
        raise DecodingError(f"Unsupported MDAT object version: {version}.")

    raw = memoryview(data)
    result = S.ChunkObjects()
    decoded: list[S.ChunkObject] = []

    with MdatReader(data) as reader:
        try:
            count = reader.varuint()
            result.count = count
            for index in range(count):
                size = reader.varuint()
                offset = reader.tell()
                end = offset + size
                if end > len(raw):
                    raise BinaryStructureError(location=reader.location, offset=offset)

                decoded.append(_object(reader, raw[offset:end], index, offset, end, version))
                reader.seek(end)

        except DecodingError as error:
            result.error = str(error)

        if result.error is None and reader.tell() != len(raw):
            result.error = "Bytes remain after declared objects"

    result.objects = tuple(decoded)
    return result
