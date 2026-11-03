import struct

from scfile.content import regions as S
from scfile.enums import F
from scfile.exceptions import DecodingError
from scfile.io.mdat import MdatReader


def _record(reader: MdatReader, raw: memoryview) -> S.ChunkRecord:
    start = reader.tell()
    kind, x, y, z, flags = struct.unpack(">biiiB", reader.read_exact(14))

    cover_count = 1
    if flags & 8:
        cover_count = 7
    covers = reader.unpack(f"{cover_count}{F.I16}")

    colors = ()
    if flags & 2:
        colors = reader.unpack(f"7{F.I16}")

    color_exponent = None
    if flags & 4:
        color_exponent = reader.value(F.I16)

    overlay = ()
    if flags & 1:
        overlay = reader.unpack(f"7{F.I8}")

    rotation = None
    if flags & 0x10:
        rotation = reader.value(F.I16)

    packed_covers = None
    if flags & 0x20:
        packed_covers = reader.value(F.I8)

    ctm = ()
    if flags & 0x40:
        ctm = reader.unpack(f"6{F.I8}")

    data = reader.value(F.I32)
    extra_data = None
    if kind == 1:
        extra_data = reader.value(F.I32)

    return S.ChunkRecord(
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


def records(raw: memoryview) -> S.ChunkRecords:
    container = S.ChunkRecords()
    entries: list[S.ChunkRecord] = []

    with MdatReader(raw.tobytes()) as reader:
        try:
            count = reader.value(F.I32)
            container.count = count

            for _ in range(count):
                entries.append(_record(reader, raw))

        except DecodingError as error:
            container.error = str(error)

        if container.error is None and reader.tell() != len(raw):
            container.error = "Bytes remain after declared records"

    container.records = tuple(entries)
    return container
