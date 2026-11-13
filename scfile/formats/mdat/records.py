import struct
from array import array

import numpy as np

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import BinaryStructureError, DecodingError
from scfile.io.mdat import MdatReader


_HEADER = struct.Struct(">biiiB")
_U16 = struct.Struct(">H")
_U32 = struct.Struct(">I")
_ZERO_U32 = b"\x00\x00\x00\x00"


def _record_sizes() -> tuple[tuple[int, int], ...]:
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
_RECORD_SIZE_0_PY = tuple(size[0] for size in _RECORD_SIZES)
_RECORD_SIZE_1_PY = tuple(size[1] for size in _RECORD_SIZES)
_RECORD_SIZE_0 = np.array([size[0] for size in _RECORD_SIZES], dtype=np.uint32)
_RECORD_SIZE_1 = np.array([size[1] for size in _RECORD_SIZES], dtype=np.uint32)
_Y_OFFSETS = np.arange(5, 9, dtype=np.uint32)
_FOUR_OFFSETS = np.arange(4, dtype=np.uint32)


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


def _append_shape_data(
    shape_data: bytearray,
    record_type: int,
    data: int,
    data_ext: int | None = None,
) -> None:
    if record_type == 1 and data_ext is not None:
        shape_data.extend(_U32.pack(data_ext & 0xFFFFFFFF))
    else:
        shape_data.extend(_ZERO_U32)
    shape_data.extend(_U32.pack(data & 0xFFFFFFFF))


def _full_records(
    raw: memoryview,
    count: int,
    container: S.ChunkRecords,
) -> S.ChunkTileMaterials | None:
    records: list[S.ChunkRecord] = []
    packed = bytearray(count * _U32.size)
    face_map = array("Q")
    shape_data = bytearray()
    record_types = bytearray()
    written = 0

    with MdatReader(raw.tobytes()) as reader:
        reader.seek(4)
        try:
            for _ in range(count):
                record_offset = reader.tell()
                record, (x, y, z, main_cover) = _record(reader, raw)
                records.append(record)

                position = _pack_position(x, y, z)
                if position is not None:
                    _U32.pack_into(packed, written * _U32.size, (position << 16) | main_cover)

                    if len(record.covers) == 7:
                        face_offset = record_offset + _HEADER.size
                        face_map.append((written << 32) | face_offset)
                        _append_shape_data(
                            shape_data,
                            record.type,
                            record.data,
                            record.data_ext,
                        )
                        record_types.append(record.type & 0xFF)

                    written += 1

        except DecodingError as error:
            container.error = str(error)

        if container.error is None and reader.tell() != len(raw):
            container.error = "Bytes remain after declared records"

    container.records = tuple(records)
    if container.error is not None or not written:
        return None

    return S.ChunkTileMaterials(
        entries=memoryview(packed)[: written * _U32.size],
        face_map=memoryview(face_map),
        shape_data=memoryview(shape_data),
        record_types=memoryview(record_types),
    )


def _fast_materials(
    raw: memoryview,
    count: int,
    container: S.ChunkRecords,
) -> S.ChunkTileMaterials | None:
    records = array("Q")
    offset = 4
    size = len(raw)

    try:
        for _ in range(count):
            if offset + _HEADER.size > size:
                raise struct.error

            kind = raw[offset]
            flags = raw[offset + 13]
            end = offset + (_RECORD_SIZE_1_PY[flags] if kind == 1 else _RECORD_SIZE_0_PY[flags])

            if end > size:
                raise struct.error

            records.append((offset << 16) | (flags << 8) | kind)
            offset = end

    except struct.error:
        container.error = str(BinaryStructureError(offset=offset))
        return None

    if offset != size:
        container.error = "Bytes remain after declared records"
        return None

    records = np.frombuffer(records, dtype=np.uint64)
    offsets = (records >> 16).astype(np.uint32)
    headers = records & 0xFFFF
    kinds = (headers & 0xFF).astype(np.uint8)
    flags_array = (headers >> 8).astype(np.uint8)
    raw_array = np.frombuffer(raw, dtype=np.uint8)
    y_bytes = raw_array[offsets[:, None] + _Y_OFFSETS]

    valid = np.all(y_bytes[:, :3] == 0, axis=1)
    if not np.any(valid):
        return None

    positions = (
        (y_bytes[:, 3].astype(np.uint32) << 8)
        | ((raw_array[offsets + 12].astype(np.uint32) & 15) << 4)
        | (raw_array[offsets + 4].astype(np.uint32) & 15)
    )
    main_offsets = offsets + np.where(flags_array & 8, 26, 14)
    main_covers = (raw_array[main_offsets].astype(np.uint16) << 8) | raw_array[main_offsets + 1].astype(np.uint16)
    entries = ((positions[valid] << 16) | main_covers[valid]).astype(">u4")

    face_records = np.flatnonzero(valid & ((flags_array & 8) != 0))
    face_map = np.empty(len(face_records), dtype=np.uint64)
    shape_data = np.empty((len(face_records), 8), dtype=np.uint8)
    record_types = kinds[face_records]

    if len(face_records):
        written_indices = np.cumsum(valid, dtype=np.uint32)[face_records] - 1
        face_offsets = offsets[face_records] + _HEADER.size
        face_map[:] = (written_indices.astype(np.uint64) << 32) | face_offsets
        ends = offsets[face_records] + np.where(
            record_types == 1,
            _RECORD_SIZE_1[flags_array[face_records]],
            _RECORD_SIZE_0[flags_array[face_records]],
        )
        kind_one = record_types == 1

        if np.any(kind_one):
            shape_data[kind_one, :4] = raw_array[ends[kind_one, None] - 4 + _FOUR_OFFSETS]
            shape_data[kind_one, 4:] = raw_array[ends[kind_one, None] - 8 + _FOUR_OFFSETS]

        if np.any(~kind_one):
            shape_data[~kind_one, :4] = 0
            shape_data[~kind_one, 4:] = raw_array[ends[~kind_one, None] - 4 + _FOUR_OFFSETS]

    return S.ChunkTileMaterials(
        entries=memoryview(entries.tobytes()),
        face_map=memoryview(face_map),
        shape_data=memoryview(shape_data.tobytes()),
        record_types=memoryview(record_types.tobytes()),
    )


def records(
    raw: memoryview,
    *,
    extended: bool = True,
) -> tuple[S.ChunkRecords, S.ChunkTileMaterials | None]:
    container = S.ChunkRecords(raw=raw)

    try:
        count = struct.unpack_from(">i", raw)[0]

    except struct.error:
        container.error = str(BinaryStructureError(offset=0))
        return container, None

    container.count = count
    if count < 0:
        container.error = "Negative records count"
        return container, None

    if count > max(0, (len(raw) - 4) // 20):
        container.error = "Record count exceeds available data"
        return container, None

    if extended:
        materials = _full_records(raw, count, container)
    else:
        materials = _fast_materials(raw, count, container)

    return container, materials
