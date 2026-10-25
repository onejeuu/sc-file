from typing import Callable
from uuid import UUID

from scfile.content import regions as S
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.base import StructReader


def varint(reader: StructReader) -> int:
    """Read the unsigned 32-bit length used by the objects list."""
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
    """Decode Java modified UTF-8, including NUL and surrogate pairs."""
    data = reader.prefixed(F.U16)
    text = data.replace(b"\xc0\x80", b"\0").decode("utf-8", errors="surrogatepass")
    return text.encode("utf-16-be", errors="surrogatepass").decode("utf-16-be", errors="surrogatepass")


def vector(reader: StructReader) -> tuple[float, float, float]:
    x, y, z = reader.unpack(f"3{F.F32}")
    return x, y, z


def instance(raw: memoryview, index: int, offset: int, header: Callable[[StructReader], S.ObjectHeader]) -> S.ChunkObject:
    result = S.ChunkObject(index, offset, raw)
    with StructReader(raw.tobytes(), order=ByteOrder.BIG) as reader:
        try:
            result.header = identity = header(reader)
            result.consumed = reader.tell()
            uuid = UUID(bytes=reader.read_exact(16))
            columns = vector(reader), vector(reader), vector(reader)
            position = vector(reader)
            result.placement = S.ObjectPlacement(uuid, columns, position)
            result.consumed = reader.tell()
            flags, flags2 = identity.flags, identity.flags2
            result.settings = S.ObjectSettings(
                active=bool(flags2 & 4),
                activation=reader.value(F.I8),
                feature_flag=java_utf(reader) if flags & 0x1000 else None,
                render_collision_status=reader.value(F.I8) if flags & 0x800 else None,
                collision_status=reader.value(F.I8),
                render_model_selection=reader.value(F.U8),
                custom_behaviour=java_utf(reader) if flags & 0x200 else None,
            )
            result.consumed = reader.tell()
        except (DecodingError, UnicodeError) as error:
            result.error = str(error)
    return result


def objects(data: bytes, header: Callable[[StructReader], S.ObjectHeader]) -> S.ChunkObjects:
    raw = memoryview(data)
    result = S.ChunkObjects(raw)
    decoded: list[S.ChunkObject] = []
    with StructReader(data, order=ByteOrder.BIG) as reader:
        try:
            result.count = varint(reader)
            result.consumed = reader.tell()
            for index in range(result.count):
                size = varint(reader)
                offset = reader.tell()
                if size > len(raw) - offset:
                    raise BinaryStructureError(location=reader.location, offset=offset)
                reader.skip(size)
                decoded.append(instance(raw[offset:reader.tell()], index, offset, header))
                result.consumed = reader.tell()
        except DecodingError as error:
            result.error = str(error)
    result.objects = tuple(decoded)
    if result.tail and result.error is None:
        result.error = "Bytes remain after declared objects"
    return result
