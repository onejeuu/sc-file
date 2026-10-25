"""Carpenters records stored after the terrain data."""

from scfile.content.regions import ChunkRecord, ChunkRecords
from scfile.enums import ByteOrder, F
from scfile.exceptions import BinaryStructureError
from scfile.io.base import StructReader


def records(raw: memoryview) -> ChunkRecords:
    result = ChunkRecords()
    reader = StructReader(raw.tobytes(), order=ByteOrder.BIG)
    decoded: list[ChunkRecord] = []
    try:
        count: int = reader.value(F.I32)
        result.count = count
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
            cover_count = 7 if flags & 8 else 1
            covers = reader.unpack(f"{cover_count}{F.I16}")

            colors: tuple[int, ...] = ()
            if flags & 2:
                colors = reader.unpack(f"7{F.I16}")

            color_exponent = None
            if flags & 4:
                color_exponent = reader.value(F.I16)

            overlay: tuple[int, ...] = ()
            if flags & 1:
                overlay = reader.unpack(f"7{F.I8}")

            rotation = None
            if flags & 0x10:
                rotation = reader.value(F.I16)

            packed_covers = None
            if flags & 0x20:
                packed_covers = reader.value(F.I8)

            ctm: tuple[int, ...] = ()
            if flags & 0x40:
                ctm = reader.unpack(f"6{F.I8}")

            data = reader.value(F.I32)
            extra_data = None
            if kind == 1:
                extra_data = reader.value(F.I32)

            decoded.append(
                ChunkRecord(
                    type=kind,
                    position=(x, y, z),
                    flags=flags,
                    covers=covers,
                    color_short=colors,
                    color_exponent=color_exponent,
                    overlay=overlay,
                    rot=rotation,
                    packcovers=packed_covers,
                    ctm_data=ctm,
                    data=data,
                    data_ext=extra_data,
                    raw=raw[start : reader.tell()],
                )
            )
    except BinaryStructureError as error:
        result.error = str(error)
    else:
        if result.error is None and reader.tell() != len(raw):
            result.error = "Bytes remain after declared records"
    finally:
        reader.close()
    result.records = tuple(decoded)
    return result
