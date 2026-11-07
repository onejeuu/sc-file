import struct

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import DecodingError
from scfile.io.mdat import MdatReader


def _record(
    reader: MdatReader,
    raw: memoryview,
    *,
    retain: bool,
) -> tuple[S.ChunkRecord | None, tuple[int, int, int, int]]:
    start = reader.tell()
    kind, x, y, z, flags = struct.unpack(">biiiB", reader.read_exact(14))

    cover_count = 7 if flags & 8 else 1
    covers = reader.unpack(f"{cover_count}{F.I16}")
    main_cover = covers[-1] & 0xFFFF

    colors = ()
    if flags & 2:
        if retain:
            colors = reader.unpack(f"7{F.I16}")
        else:
            reader.read_exact(14)

    color_exponent = None
    if flags & 4:
        if retain:
            color_exponent = reader.value(F.I16)
        else:
            reader.read_exact(2)

    overlay = ()
    if flags & 1:
        if retain:
            overlay = reader.unpack(f"7{F.I8}")
        else:
            reader.read_exact(7)

    rotation = None
    if flags & 0x10:
        if retain:
            rotation = reader.value(F.I16)
        else:
            reader.read_exact(2)

    packed_covers = None
    if flags & 0x20:
        if retain:
            packed_covers = reader.value(F.I8)
        else:
            reader.read_exact(1)

    ctm = ()
    if flags & 0x40:
        if retain:
            ctm = reader.unpack(f"6{F.I8}")
        else:
            reader.read_exact(6)

    data = reader.value(F.I32)
    extra_data = None
    if kind == 1:
        extra_data = reader.value(F.I32)

    record = None
    if retain:
        record = S.ChunkRecord(
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

    return record, (x, y, z, main_cover)


def records(
    raw: memoryview,
    *,
    include_records: bool = True,
) -> tuple[S.ChunkRecords, S.ChunkTileMaterials | None]:
    container = S.ChunkRecords()
    entries: list[S.ChunkRecord] = []
    positions = bytearray()
    states = bytearray()

    with MdatReader(raw.tobytes()) as reader:
        try:
            count = reader.value(F.I32)
            container.count = count

            if count < 0:
                container.error = "Negative records count"
            elif count > max(0, (len(raw) - 4) // 20):
                container.error = "Record count exceeds available data"
            else:
                positions = bytearray(count * 12)
                states = bytearray(count * 2)

                for index in range(count):
                    record, (x, y, z, main_cover) = _record(reader, raw, retain=include_records)
                    if record is not None:
                        entries.append(record)

                    struct.pack_into(">3i", positions, index * 12, x, y, z)
                    struct.pack_into(">H", states, index * 2, main_cover)

        except DecodingError as error:
            container.error = str(error)

        if container.error is None and reader.tell() != len(raw):
            container.error = "Bytes remain after declared records"

    container.records = tuple(entries)
    materials = None
    if container.error is None and container.count:
        materials = S.ChunkTileMaterials(memoryview(positions), memoryview(states))

    return container, materials
