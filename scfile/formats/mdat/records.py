from scfile.content.regions import ChunkRecord, ChunkRecords
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError
from scfile.io.base import StructReader


def records(raw: memoryview) -> ChunkRecords:
    result = ChunkRecords(raw)
    reader = StructReader(raw.tobytes(), order=ByteOrder.BIG)
    decoded: list[ChunkRecord] = []
    try:
        count: int = reader.value(F.I32)
        result.count = count
        result.consumed = reader.tell()
        if count < 0:
            result.error = "Negative records count"
            return result
        for _ in range(count):
            start = reader.tell()
            kind, x, y, z = reader.unpack(f"{F.I8}3{F.I32}")
            if kind not in (0, 1):
                result.error = f"Unknown record type {kind}; boundary unavailable"
                break
            flags = reader.value(F.U8)
            if flags & 0x80:
                result.error = "Unknown record flag bit; boundary unavailable"
                break
            decoded.append(ChunkRecord(
                type=kind,
                position=(x, y, z),
                flags=flags,
                covers=reader.unpack(f"{7 if flags & 8 else 1}{F.I16}"),
                color_short=reader.unpack(f"7{F.I16}") if flags & 2 else (),
                color_exponent=reader.value(F.I16) if flags & 4 else None,
                overlay=reader.unpack(f"7{F.I8}") if flags & 1 else (),
                rot=reader.value(F.I16) if flags & 0x10 else None,
                packcovers=reader.value(F.I8) if flags & 0x20 else None,
                ctm_data=reader.unpack(f"6{F.I8}") if flags & 0x40 else (),
                data=reader.value(F.I32),
                data_ext=reader.value(F.I32) if kind == 1 else None,
                raw=raw[start:reader.tell()],
            ))
            result.consumed = reader.tell()
    except BinaryStructureError as error:
        result.error = str(error)
    finally:
        reader.close()
    result.records = tuple(decoded)
    if result.tail and result.error is None:
        result.error = "Bytes remain after declared records"
    return result
