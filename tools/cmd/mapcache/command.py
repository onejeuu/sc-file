from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from itertools import islice
from pathlib import Path
from typing import Any

import click
from rich.console import Console

from tools.cmd import tools
from tools.paths import ROOT

from . import census, compare, inspect, maps, metadata, reports, search, tables
from .inspect import RecordDetails
from .mdat import records
from .mdat.models import Block, Chunk, Location
from .mdat.reader import Region, paths
from .mdat.terrain import Terrain
from .metadata import BlockDefinition, Catalog
from .reports import ChunkInfo, Diagnostic, RegionInfo


SOURCE = click.Path(path_type=Path, exists=True)
REGION = click.Path(path_type=Path, exists=True, dir_okay=False)
OUTPUT = click.Path(path_type=Path, file_okay=False)
REPORTS = ROOT / "reports" / "mapcache"


def io_errors[**P, T](callback: Callable[P, T]) -> Callable[P, T]:
    @wraps(callback)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return callback(*args, **kwargs)
        except OSError as error:
            raise click.ClickException(str(error)) from None

    return wrapped


def selection(callback: Callable[..., Any]) -> Callable[..., Any]:
    callback = click.option("--chunk", "position", nargs=2, type=int, help="World chunk X Z, alternative to --index.")(
        callback
    )
    return click.option("--index", type=click.IntRange(0, 1023), help="Table index: localX + localZ * 32.")(callback)


def json_option(callback: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "as_json", is_flag=True, help="Print JSON instead of Rich tables.")(callback)


def xeon_option(callback: Callable[..., Any]) -> Callable[..., Any]:
    return click.option(
        "--xeon",
        type=click.Path(path_type=Path, exists=True, file_okay=False),
        help="Unpacked xeon root for block metadata and object registry candidates.",
    )(callback)


def catalog_from(path: Path | None) -> Catalog | None:
    return metadata.load(path) if path is not None else None


class Number(click.ParamType):
    name = "integer/hex"

    def __init__(self, maximum: int):
        self.maximum = maximum

    def convert(self, value: Any, param: click.Parameter | None, ctx: click.Context | None) -> int:
        try:
            text = str(value)
            number = int(text, 16 if text.lower().startswith("0x") else 10)
        except ValueError:
            self.fail("Use decimal or 0x-prefixed hexadecimal", param, ctx)
        if not 0 <= number <= self.maximum:
            self.fail(f"Value must be 0..{self.maximum}", param, ctx)
        return number


def selected(source: Path, index: int | None, position: tuple[int, int] | None) -> tuple[Region, Chunk]:
    region = Region(source)
    if position is not None:
        if index is not None or region.coordinates is None:
            raise click.UsageError("--chunk requires a region filename and cannot be combined with --index")
        rx, rz = region.coordinates
        x, z = position[0] - rx * 32, position[1] - rz * 32
        if not (0 <= x < 32 and 0 <= z < 32):
            raise click.UsageError("Chunk coordinates do not belong to this region")
        index = x + z * 32
    if index is None:
        raise click.UsageError("Select --index or --chunk X Z")
    if index >= len(region.entries):
        raise click.UsageError("Selected table entry is unavailable")
    return region, region.chunk(index)


def require_source(source: Path) -> None:
    if not paths(source):
        raise click.UsageError(f"No MDAT files in {source}")


def print_json(value: object) -> None:
    click.echo(reports.text(value))


def print_notes(values: list[Diagnostic]) -> None:
    if values:
        Console().print(tables.notes(values))


@tools.group()
def mapcache() -> None:
    """Inspect MDAT bytes, full terrain states, Carpenters, and object instances."""


@dataclass(frozen=True)
class RegionView:
    region: RegionInfo
    entries: list[ChunkInfo]


@mapcache.command("region")
@click.argument("source", type=REGION)
@click.option("--all", "all_entries", is_flag=True, help="Include unoccupied table cells.")
@json_option
@io_errors
def region_command(source: Path, all_entries: bool, as_json: bool) -> None:
    """Show the location table and chunk headers without decompression."""
    region = Region(source)
    rows = [
        reports.chunk_info(region, region.chunk(entry.index, decode=False))
        for entry in region.entries
        if all_entries or entry.present
    ]
    if as_json:
        print_json(RegionView(reports.region_info(region), rows))
        return
    console = Console()
    console.print(
        tables.details(
            (
                ("Path", region.path),
                ("Region", region.coordinates),
                ("Bytes", len(region.raw)),
                ("Occupied", sum(entry.present for entry in region.entries)),
            )
        )
    )
    console.print(tables.region(rows))
    notes = [Diagnostic(region.path, None, note) for note in region.notes]
    notes.extend(Diagnostic(region.path, row.entry.index, note) for row in rows for note in row.notes)
    print_notes(notes)


@mapcache.command("chunk")
@click.argument("source", type=REGION)
@selection
@json_option
@io_errors
def chunk_command(source: Path, index: int | None, position: tuple[int, int] | None, as_json: bool) -> None:
    """Show masks, frame boundaries, terrain planes, and container counts."""
    region, chunk = selected(source, index, position)
    value = inspect.overview(region, chunk)
    if as_json:
        print_json(value)
        return
    console = Console()
    console.print(tables.chunk(value))
    console.print(tables.terrain(value))
    notes = region.notes + chunk.notes
    if value.terrain is not None:
        notes += value.terrain.notes
    if value.records is not None:
        notes += value.records.notes
    if value.objects is not None:
        notes += value.objects.notes
    print_notes([Diagnostic(region.path, chunk.entry.index, note) for note in notes])


@dataclass(frozen=True)
class BlockView:
    location: Location
    block: Block
    definition: BlockDefinition | None
    records: list[RecordDetails]
    notes: list[Diagnostic]


@mapcache.command("block", context_settings={"ignore_unknown_options": True})
@click.argument("source", type=REGION)
@click.argument("x", type=int)
@click.argument("y", type=click.IntRange(0, 255))
@click.argument("z", type=int)
@click.option("--local", is_flag=True, help="Use local x/z 0..15 and select a chunk.")
@selection
@xeon_option
@json_option
@io_errors
def block_command(
    source: Path,
    x: int,
    y: int,
    z: int,
    local: bool,
    index: int | None,
    position: tuple[int, int] | None,
    xeon: Path | None,
    as_json: bool,
) -> None:
    """Inspect full state, biome, lighting, offsets, and original nibble bytes."""
    if local:
        if not (0 <= x < 16 and 0 <= z < 16):
            raise click.UsageError("Local x/z must be 0..15")
        region, chunk = selected(source, index, position)
    else:
        if index is not None or position is not None:
            raise click.UsageError("World coordinates select the chunk; --index/--chunk require --local")
        cx, x = divmod(x, 16)
        cz, z = divmod(z, 16)
        region, chunk = selected(source, None, (cx, cz))
    terrain = Terrain.from_chunk(chunk)
    if terrain is None:
        print_json(inspect.overview(region, chunk))
        return
    block = terrain.block((x, y, z), chunk)
    catalog = catalog_from(xeon)
    container = records.read(terrain.records)
    associated = [
        inspect.record_details(record, chunk, terrain, catalog)
        for record in container.items
        if record.header.position == block.world
    ]
    notes = [
        Diagnostic(region.path, chunk.entry.index, note)
        for note in region.notes + chunk.notes + terrain.notes + container.notes
    ]
    if catalog is not None:
        notes.extend(catalog.notes)
    definition = catalog.block(block.state) if catalog is not None and block.state is not None else None
    if as_json:
        print_json(BlockView(region.location(chunk.entry.index), block, definition, associated, notes))
        return
    state = block.state
    Console().print(
        tables.details(
            (
                ("World block", block.world),
                ("Local block", block.local),
                ("Status", block.status),
                ("State", f"0x{state.value:04x}" if state else None),
                ("Block ID", state.block_id if state else None),
                ("Metadata", state.metadata if state else None),
                ("Icon", definition.icon if definition else None),
            )
        )
    )
    Console().print(tables.block(block))
    for record in associated:
        Console().print(tables.carpenter(record))
        Console().print(tables.faces(record.carpenter))
    print_notes(notes)


@mapcache.command("records")
@click.argument("source", type=REGION)
@selection
@xeon_option
@click.option("--record", type=click.IntRange(min=0), help="Inspect one complete record with raw bytes.")
@click.option("--limit", type=click.IntRange(min=1), default=20, show_default=True)
@json_option
@io_errors
def records_command(
    source: Path,
    index: int | None,
    position: tuple[int, int] | None,
    xeon: Path | None,
    record: int | None,
    limit: int,
    as_json: bool,
) -> None:
    """Read the confirmed record layout; retain an unknown remainder."""
    region, chunk = selected(source, index, position)
    catalog = catalog_from(xeon)
    try:
        value = inspect.record_view(region, chunk, record, limit, catalog)
    except IndexError:
        raise click.UsageError("Requested record is not available as a complete record") from None
    if value is None:
        print_json(inspect.overview(region, chunk))
    elif as_json or record is not None:
        print_json(value)
    else:
        Console().print(
            tables.details(
                (
                    ("Path", region.path),
                    ("Chunk", chunk.coordinates),
                    ("Declared", value.container.declared),
                    ("Parsed", value.container.parsed),
                    ("Unparsed bytes", value.container.tail.size),
                )
            )
        )
        Console().print(tables.records(value))
        print_notes(
            [Diagnostic(region.path, chunk.entry.index, note) for note in chunk.notes + value.container.notes]
            + value.metadata_notes
        )


@mapcache.command("objects")
@click.argument("source", type=REGION)
@selection
@xeon_option
@click.option("--item", type=click.IntRange(min=0))
@click.option("--limit", type=click.IntRange(min=1), default=20, show_default=True)
@json_option
@io_errors
def objects_command(
    source: Path,
    index: int | None,
    position: tuple[int, int] | None,
    item: int | None,
    limit: int,
    xeon: Path | None,
    as_json: bool,
) -> None:
    """Read instance fields and transforms; resolve definition candidates with xeon."""
    region, chunk = selected(source, index, position)
    catalog = catalog_from(xeon)
    try:
        value = inspect.object_view(region, chunk, item, limit, catalog)
    except IndexError:
        raise click.UsageError("Requested object item is not available") from None
    if value is None:
        print_json(inspect.overview(region, chunk))
    elif as_json or item is not None:
        print_json(value)
    else:
        Console().print(
            tables.details(
                (
                    ("Path", region.path),
                    ("Chunk", chunk.coordinates),
                    ("Declared", value.container.declared),
                    ("Parsed", value.container.parsed),
                    ("Unparsed bytes", value.container.tail.size),
                )
            )
        )
        Console().print(tables.objects(value))
        print_notes(
            [Diagnostic(region.path, chunk.entry.index, note) for note in chunk.notes + value.container.notes]
            + value.metadata_notes
        )


@mapcache.command("dump")
@click.argument("source", type=REGION)
@selection
@click.option("-o", "--output", type=OUTPUT, required=True, help="Empty directory for this chunk's artifacts.")
@json_option
@io_errors
def dump_command(
    source: Path, index: int | None, position: tuple[int, int] | None, output: Path, as_json: bool
) -> None:
    """Write frames, header + terrain payload, planes, and a source manifest."""
    region, chunk = selected(source, index, position)
    value = inspect.dump(region, chunk, output)
    if as_json:
        print_json(value)
    else:
        Console().print(
            tables.details(
                (
                    ("Source", region.path),
                    ("Index", chunk.entry.index),
                    ("Output", output.resolve()),
                    ("Files", len(value.files)),
                )
            )
        )


@mapcache.command("census")
@click.argument("source", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "census", show_default=True)
@click.option("--details", is_flag=True, help="Also write each chunk's metadata to JSONL.")
@xeon_option
@json_option
@io_errors
def census_command(source: Path, output: Path, details: bool, xeon: Path | None, as_json: bool) -> None:
    """Write state, biome, record, and interpreted object statistics to JSON."""
    require_source(source)
    value = census.run(source, output, details=details, catalog=catalog_from(xeon))
    if as_json:
        print_json(value.totals)
    else:
        total = value.totals
        Console().print(
            tables.details(
                (
                    ("Regions", total.regions),
                    ("Chunks", total.chunks),
                    ("Stored voxels", total.stored_voxels),
                    ("States", len(value.states)),
                    ("Records", total.records),
                    ("Objects", total.objects),
                    ("Instances read", total.instances_read),
                    ("Instance unparsed bytes", total.instance_unparsed_bytes),
                    ("Notes", len(value.notes)),
                    ("Report", (output / "census.json").resolve()),
                )
            )
        )
        print_notes(value.metadata_notes)


@mapcache.command("compare")
@click.argument("before", type=SOURCE)
@click.argument("after", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "compare", show_default=True)
@io_errors
def compare_command(before: Path, after: Path, output: Path) -> None:
    """Compare payload hashes and UUIDs within maps with the same name."""
    require_source(before)
    require_source(after)
    print_json(compare.run(before, after, output))


@mapcache.command("metadata")
@click.argument("source", type=click.Path(path_type=Path, exists=True, file_okay=False))
@click.option("-o", "--output", type=click.Path(path_type=Path, dir_okay=False), required=True)
@io_errors
def metadata_command(source: Path, output: Path) -> None:
    """Write current block metadata and sorted object registry candidates from xeon."""
    catalog = metadata.load(source)
    reports.write(output, catalog)
    Console().print(
        tables.details(
            (
                ("Block states", len(catalog.blocks)),
                ("Object candidates", len(catalog.objects)),
                ("Notes", len(catalog.notes)),
                ("Output", output.resolve()),
            )
        )
    )
    print_notes(catalog.notes)


@mapcache.command("map")
@click.argument("source", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "maps", show_default=True)
@click.option("--min-y", type=click.IntRange(0, 255), default=0, show_default=True)
@click.option("--max-y", type=click.IntRange(0, 255), default=255, show_default=True)
@click.option("--ignore-block", type=Number(4095), multiple=True, help="Explicit full block IDs to skip.")
@click.option("--max-pixels", type=click.IntRange(min=256), default=16777216, show_default=True)
@io_errors
def map_command(
    source: Path, output: Path, min_y: int, max_y: int, ignore_block: tuple[int, ...], max_pixels: int
) -> None:
    """Write diagnostic height/state PNG and exact surface arrays per map folder."""
    require_source(source)
    if min_y > max_y:
        raise click.UsageError("--min-y must not exceed --max-y")
    for value in maps.run(source, output, min_y, max_y, ignore_block, max_pixels):
        Console().print(
            tables.details(
                (
                    ("Source", value.source),
                    ("Output", value.output),
                    ("Origin X/Z", value.origin),
                    ("Size", value.size),
                    ("Notes", len(value.notes)),
                )
            )
        )


@dataclass(frozen=True)
class SearchResult:
    matches: int
    limit_reached: bool
    notes: list[Diagnostic]


@mapcache.command("find")
@click.argument("source", type=SOURCE)
@click.option("--state", type=Number(65535))
@click.option("--block-id", type=Number(4095))
@click.option("--record-type", type=click.IntRange(-128, 127))
@click.option("--object-prefix", type=Number(65535))
@click.option("--object-id", help="Exact definition candidate from --xeon.")
@xeon_option
@click.option("--text", help="Find literal UTF-8 bytes in raw object items.")
@click.option("--limit", type=click.IntRange(min=1), default=100, show_default=True)
@click.option("-o", "--output", type=click.Path(path_type=Path, dir_okay=False))
@io_errors
def find_command(
    source: Path,
    state: int | None,
    block_id: int | None,
    record_type: int | None,
    object_prefix: int | None,
    object_id: str | None,
    xeon: Path | None,
    text: str | None,
    limit: int,
    output: Path | None,
) -> None:
    """Emit JSONL matches with typed data and source addresses."""
    catalog = catalog_from(xeon)
    if object_id is not None:
        if catalog is None or not catalog.registry_complete:
            raise click.UsageError("--object-id requires a complete --xeon catalog")
        if object_prefix is not None:
            raise click.UsageError("Use either --object-id or --object-prefix")
        definition = next((row for row in catalog.objects if row.object_id == object_id), None)
        if definition is None:
            raise click.UsageError(f"Unknown object_id {object_id}")
        object_prefix = definition.network_id_candidate
    if all(value is None for value in (state, block_id, record_type, object_prefix, text)):
        raise click.UsageError("Specify a state, block ID, record type, object prefix, or literal text")
    require_source(source)
    if output is not None and output.resolve() in (path.resolve() for path in paths(source)):
        raise click.UsageError("Output must differ from the input files")
    query = search.Query(
        state, block_id, record_type, object_prefix, text.encode("utf-8") if text is not None else None
    )
    notes: list[Diagnostic] = list(catalog.notes) if catalog is not None else []
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
    with click.open_file(str(output) if output is not None else "-", "w", encoding="utf-8") as stream:
        count = 0
        for hit in islice(search.find(source, query, notes, catalog), limit):
            stream.write(reports.line(hit) + "\n")
            count += 1
        stream.write(reports.line(SearchResult(count, count == limit, notes)) + "\n")
