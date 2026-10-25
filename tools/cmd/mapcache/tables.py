from collections.abc import Iterable

from rich.table import Table
from rich.text import Text

from .carpenters import Carpenter
from .inspect import ObjectsView, Overview, RecordDetails, RecordView
from .mdat.models import Block
from .reports import ChunkInfo, Diagnostic


def details(rows: Iterable[tuple[str, object]]) -> Table:
    table = Table(box=None, show_header=False)
    table.add_column(style="cyan")
    table.add_column()
    for name, value in rows:
        table.add_row(name, Text(str(value)))
    return table


def region(rows: list[ChunkInfo]) -> Table:
    table = Table("Index", "Chunk X/Z", "Sector", "Sectors", "Section mask", "Add mask", "Terrain ZSTD", "Objects ZSTD")
    for row in rows:
        header = row.header
        table.add_row(
            str(row.entry.index),
            str(row.location.chunk),
            str(row.entry.sector),
            str(row.entry.sectors),
            f"{header.section_mask & 65535:04x}" if header else "",
            f"{header.add_mask & 65535:04x}" if header else "",
            str(header.compressed_size) if header else "",
            str(row.objects.compressed.size) if row.objects else "",
        )
    return table


def records(view: RecordView) -> Table:
    table = Table("Record", "Type", "World X/Y/Z", "Flags", "Bytes", "Terrain offset", "Data", "Data ext")
    for row in view.items:
        record = row.record
        table.add_row(
            str(record.index),
            str(record.header.type),
            str(record.header.position),
            f"0x{record.payload.flags:02x}",
            str(record.raw.size),
            str(record.raw.offset),
            str(record.payload.data),
            str(record.payload.data_ext) if record.payload.data_ext is not None else "",
        )
    return table


def objects(view: ObjectsView) -> Table:
    table = Table("Item", "Network ID", "Definition candidate", "UUID", "Position", "Unparsed bytes")
    for row in view.items:
        placement = row.instance.placement
        table.add_row(
            str(row.item.index),
            str(row.item.prefix),
            row.definition.object_id if row.definition else "",
            str(placement.uuid) if placement is not None else "",
            str(placement.position) if placement is not None else "",
            str(row.instance.tail.size),
        )
    return table


def carpenter(value: RecordDetails) -> Table:
    return details(
        (
            ("Record", value.record.index),
            ("Block ID", value.state.block_id if value.state else None),
            ("Shape", value.carpenter.shape),
        )
    )


def faces(value: Carpenter) -> Table:
    table = Table("Side", "Cover", "Icon", "Tint", "Exp", "Overlay", "UV", "CTM", "Packed")
    for index in (0, 1, 3):
        table.columns[index].no_wrap = True
    for face in value.faces:
        table.add_row(
            face.side,
            f"0x{face.cover.value:04x}",
            face.definition.icon if face.definition else "",
            f"{face.color_rgb565:04x}" if face.color_rgb565 is not None else "",
            str(face.color_exponent),
            str(face.overlay),
            str(face.rotation_quarters) if face.rotation_quarters is not None else "",
            f"{face.ctm_data:02x}" if face.ctm_data is not None else "",
            "yes" if face.packed else "no",
        )
    return table


def block(value: Block) -> Table:
    table = Table("Plane", "Terrain offset", "Byte", "Nibble", "Value")
    for sample in value.samples:
        table.add_row(
            sample.plane,
            str(sample.offset) if sample.offset is not None else "",
            f"{sample.byte:02x}" if sample.byte is not None else "",
            sample.nibble or "",
            str(sample.value) if sample.value is not None else "",
        )
    return table


def chunk(value: Overview) -> Table:
    row = value.chunk
    return details(
        (
            ("Path", row.location.path),
            ("Chunk", row.location.chunk),
            ("Index", row.entry.index),
            ("Sector", row.entry.sector),
            ("Sectors", row.entry.sectors),
            ("UUID", row.uuid),
            ("Header", row.header),
            ("Terrain bytes", row.terrain.decompressed_size if row.terrain else None),
            ("Objects bytes", row.objects.decompressed_size if row.objects else None),
            ("Records", value.records.declared if value.records else None),
            ("Object items", value.objects.declared if value.objects else None),
        )
    )


def terrain(value: Overview) -> Table:
    table = Table("Plane", "Terrain offset", "Declared bytes", "Available bytes")
    if value.terrain is not None:
        for plane in value.terrain.planes:
            table.add_row(plane.name, str(plane.range.offset), str(plane.range.size), str(plane.range.available))
    return table


def notes(values: list[Diagnostic]) -> Table:
    table = Table("Source", "Chunk index", "Buffer", "Offset", "Note")
    for item in values:
        table.add_row(
            Text(str(item.path)), str(item.index), item.note.buffer, str(item.note.offset), Text(item.note.message)
        )
    return table
