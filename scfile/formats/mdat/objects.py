"""Objects stored alongside terrain in MDAT 6 and 7."""

from uuid import UUID

from scfile.content import regions as S
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.base import StructReader


def object_header(reader: StructReader, version: int) -> S.ObjectHeader:
    match version:
        case 6:
            type_id = reader.value(F.U16)
        case 7:
            type_id = reader.value(F.U64)
        case _:
            raise DecodingError(
                f"Unsupported MDAT object version: {version}",
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
        java_utf(reader)
    if flags & 0x4000:
        reader.skip(4)
    if flags & 0x2000:
        reader.skip(4)
    if version == 6:
        reader.skip(4)

    return S.ObjectHeader(type_id, flags, flags2, group)


def varint(reader: StructReader) -> int:
    value = 0
    for shift in range(0, 35, 7):
        byte = reader.value(F.U8)
        if shift == 28 and byte & 0xF0:
            raise BinaryStructureError(location=reader.location, offset=reader.tell() - 1)
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value
    raise BinaryStructureError(location=reader.location, offset=reader.tell())


def java_utf(reader: StructReader) -> str:
    data = reader.prefixed(F.U16)
    text = data.replace(b"\xc0\x80", b"\0").decode("utf-8", errors="surrogatepass")
    return text.encode("utf-16-be", errors="surrogatepass").decode("utf-16-be", errors="surrogatepass")


def vector(reader: StructReader) -> S.Vector3:
    return reader.unpack(f"3{F.F32}")


def instance(raw: memoryview, index: int, offset: int, version: int) -> S.ChunkObject:
    result = S.ChunkObject(index, offset, raw)
    with StructReader(raw.tobytes(), order=ByteOrder.BIG) as reader:
        try:
            header = object_header(reader, version)
            result.header = header
            uuid = UUID(bytes=reader.read_exact(16))
            matrix = (vector(reader), vector(reader), vector(reader))
            position = vector(reader)
            result.placement = S.ObjectPlacement(uuid, matrix, position)

            flags, flags2 = header.flags, header.flags2
            result.settings = S.ObjectSettings(
                active=bool(flags2 & 4),
                activation=reader.value(F.I8),
                feature_flag=java_utf(reader) if flags & 0x1000 else None,
                render_collision_status=reader.value(F.I8) if flags & 0x800 else None,
                collision_status=reader.value(F.I8),
                render_model_selection=reader.value(F.U8),
                custom_behaviour=java_utf(reader) if flags & 0x200 else None,
            )
        except (DecodingError, UnicodeError) as error:
            result.error = str(error)
    return result


def objects(data: bytes, version: int) -> S.ChunkObjects:
    raw = memoryview(data)
    result = S.ChunkObjects()
    decoded: list[S.ChunkObject] = []
    with StructReader(data, order=ByteOrder.BIG) as reader:
        try:
            result.count = varint(reader)
            for index in range(result.count):
                size = varint(reader)
                offset = reader.tell()
                if size > len(raw) - offset:
                    raise BinaryStructureError(location=reader.location, offset=offset)
                reader.skip(size)
                decoded.append(instance(raw[offset : reader.tell()], index, offset, version))
        except DecodingError as error:
            result.error = str(error)
        else:
            if reader.tell() != len(raw):
                result.error = "Bytes remain after declared objects"

    result.objects = tuple(decoded)
    return result
