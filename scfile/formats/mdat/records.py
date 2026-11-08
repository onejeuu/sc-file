import struct

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.mdat import MdatReader


_HEADER = struct.Struct(">biiiB")
_U16 = struct.Struct(">H")
_U32 = struct.Struct(">I")


def _record_sizes() -> tuple[tuple[int, int], ...]:
    """Precompute encoded record sizes for every possible flags byte."""
    sizes = []
    for flags in range(256):
        size = (
            _HEADER.size
            + (14 if flags & 8 else 2)
            + (14 if flags & 2 else 0)
            + (2 if flags & 4 else 0)
            + (7 if flags & 1 else 0)
            + (2 if flags & 0x10 else 0)
            + (1 if flags & 0x20 else 0)
            + (6 if flags & 0x40 else 0)
            + 4
        )
        sizes.append((size, size + 4))
    return tuple(sizes)


_RECORD_SIZES = _record_sizes()


def _pack_position(x: int, y: int, z: int) -> int | None:
    if not 0 <= y < 256:
        return None

    return (y << 8) | ((z & 15) << 4) | (x & 15)


def _record(
    reader: MdatReader,
    raw: memoryview,
) -> tuple[S.ChunkRecord, tuple[int, int, int, int]]:
    start = reader.tell()
    kind, x, y, z, flags = _HEADER.unpack(reader.read_exact(_HEADER.size))

    cover_count = 7 if flags & 8 else 1
    covers = reader.unpack(f"{cover_count}{F.I16}")
    main_cover = covers[-1] & 0xFFFF

    colors = reader.unpack(f"7{F.I16}") if flags & 2 else ()
    color_exponent = reader.value(F.I16) if flags & 4 else None
    overlay = reader.unpack(f"7{F.I8}") if flags & 1 else ()
    rotation = reader.value(F.I16) if flags & 0x10 else None
    packed_covers = reader.value(F.I8) if flags & 0x20 else None
    ctm = reader.unpack(f"6{F.I8}") if flags & 0x40 else ()

    data = reader.value(F.I32)
    extra_data = reader.value(F.I32) if kind == 1 else None

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


def _fast_materials(
    raw: memoryview,
    count: int,
    container: S.ChunkRecords,
) -> S.ChunkTileMaterials | None:
    entries = bytearray(count * _U32.size)
    offset = 4
    written = 0
    size = len(raw)

    try:
        for _ in range(count):
            kind, x, y, z, flags = _HEADER.unpack_from(raw, offset)
            record_size = _RECORD_SIZES[flags][kind == 1]
            end = offset + record_size
            if end > size:
                raise struct.error

            cover_offset = offset + _HEADER.size + (12 if flags & 8 else 0)
            main_cover = _U16.unpack_from(raw, cover_offset)[0]
            position = _pack_position(x, y, z)
            if position is not None:
                _U32.pack_into(entries, written * _U32.size, (position << 16) | main_cover)
                written += 1

            offset = end

    except struct.error:
        container.error = str(BinaryStructureError(offset=offset))
        return None

    if offset != size:
        container.error = "Bytes remain after declared records"
        return None

    if not written:
        return None

    return memoryview(entries)[: written * _U32.size]


def _full_records(
    raw: memoryview,
    count: int,
    container: S.ChunkRecords,
) -> S.ChunkTileMaterials | None:
    records: list[S.ChunkRecord] = []
    packed = bytearray(count * _U32.size)
    written = 0

    with MdatReader(raw.tobytes()) as reader:
        reader.seek(4)
        try:
            for _ in range(count):
                record, (x, y, z, main_cover) = _record(reader, raw)
                records.append(record)

                position = _pack_position(x, y, z)
                if position is not None:
                    _U32.pack_into(packed, written * _U32.size, (position << 16) | main_cover)
                    written += 1

        except DecodingError as error:
            container.error = str(error)

        if container.error is None and reader.tell() != len(raw):
            container.error = "Bytes remain after declared records"

    container.records = tuple(records)
    if container.error is not None or not written:
        return None

    return memoryview(packed)[: written * _U32.size]


def records(
    raw: memoryview,
    *,
    include: bool = True,
) -> tuple[S.ChunkRecords, S.ChunkTileMaterials | None]:
    container = S.ChunkRecords()

    try:
        count = struct.unpack_from(">i", raw)[0]
    except struct.error:
        container.error = str(BinaryStructureError(offset=0))
        return container, None

    container.count = count
    if count < 0:
        container.error = "Negative records count"
        return container, None

    # The smallest record is its 14-byte header, one cover, and a 4-byte data field.
    if count > max(0, (len(raw) - 4) // 20):
        container.error = "Record count exceeds available data"
        return container, None

    if include:
        materials = _full_records(raw, count, container)
    else:
        materials = _fast_materials(raw, count, container)

    return container, materials

