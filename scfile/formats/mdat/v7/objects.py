from uuid import UUID

from scfile.content.regions import ObjectHeader
from scfile.enums import F
from scfile.exceptions import DecodingError
from scfile.io.base import StructReader

from ..objects import java_utf


def header(reader: StructReader) -> ObjectHeader:
    type_hash = reader.value(F.U64)
    flags, flags2 = reader.unpack(f"{F.U32}{F.U8}")
    if flags & ~0x3FBFF or flags2 & ~7:
        raise DecodingError(
            "Unknown object flags; header boundary unavailable", location=reader.location, offset=reader.tell()
        )
    group = UUID(bytes=reader.read_exact(16)) if flags & 0x80 else None
    patch = java_utf(reader) if flags & 0x8000 else None
    csv = reader.value(F.I32) if flags & 0x4000 else None
    cbv = reader.value(F.I32) if flags & 0x2000 else None
    return ObjectHeader(None, type_hash, flags, flags2, group, patch, csv, cbv, None)
