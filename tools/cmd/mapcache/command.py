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
from .mdat.models import Chunk, Location
from .mdat.reader import Region, paths
from .mdat.terrain import Block, Terrain
from .mdat.versions import SUPPORTED_VERSIONS
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
    callback = click.option(
        "--chunk", "position", nargs=2, type=int, help="World chunk coordinates X Z. Use instead of --index."
    )(callback)
    return click.option("--index", type=click.IntRange(0, 1023), help="Table index: local X + local Z * 32.")(callback)


def json_option(callback: Callable[..., Any]) -> Callable[..., Any]:
    return click.option("--json", "as_json", is_flag=True, help="Output as JSON.")(callback)


def catalog_from() -> Catalog:
    return metadata.load()


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
    region = Region(source, _version())
    if position is not None:
        if index is not None or region.coordinates is None:
            raise click.UsageError("--chunk requires a region filename and cannot be combined with --index")

        rx, rz = region.coordinates
        x, z = position[0] - rx * 32, position[1] - rz * 32

        if not (0 <= x < 32 and 0 <= z < 32):
            raise click.UsageError("Chunk coordinates do not belong to this region")

        index = x + z * 32

    if index is None:
        raise click.UsageError("Use --index or --chunk X Z")

    if index >= len(region.entries):
        raise click.UsageError("The selected table entry does not exist")

    return region, region.chunk(index)


def require_source(source: Path) -> None:
    if not paths(source):
        raise click.UsageError(f"No MDAT files found in {source}")


def print_json(value: object) -> None:
    click.echo(reports.text(value))


def print_notes(values: list[Diagnostic]) -> None:
    if values:
        Console().print(tables.notes(values))


@tools.group(help="Inspect MDAT files, terrain states, block shapes, and object instances.")
@click.option(
    "--mdat-version",
    type=click.IntRange(min(SUPPORTED_VERSIONS), max(SUPPORTED_VERSIONS)),
    help="MDAT major version. Defaults to the newest supported version.",
)
@click.pass_context
def mapcache(ctx: click.Context, mdat_version: int | None) -> None:
    ctx.ensure_object(dict)["mdat_version"] = mdat_version


def _version() -> int | None:
    return click.get_current_context().obj.get("mdat_version")


@dataclass(frozen=True)
class RegionView:
    region: RegionInfo
    entries: list[ChunkInfo]


@mapcache.command("region", help="Show the location table and chunk headers without decompressing data.")
@click.argument("source", type=REGION)
@click.option("--all", "all_entries", is_flag=True, help="Include empty table cells.")
@json_option
@io_errors
def region_command(source: Path, all_entries: bool, as_json: bool) -> None:
    region = Region(source, _version())
    rows = [
        reports.chunk_info(region, region.chunk(entry.index))
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


@mapcache.command("chunk", help="Show masks, frame boundaries, terrain planes, and record and object counts.")
@click.argument("source", type=REGION)
@selection
@json_option
@io_errors
def chunk_command(source: Path, index: int | None, position: tuple[int, int] | None, as_json: bool) -> None:
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


@mapcache.command(
    "block",
    context_settings={"ignore_unknown_options": True},
    help="Show block state, biome, lighting, offsets, and raw nibble data.",
)
@click.argument("source", type=REGION)
@click.argument("x", type=int)
@click.argument("y", type=click.IntRange(0, 255))
@click.argument("z", type=int)
@click.option("--local", is_flag=True, help="Treat x/z as local coordinates from 0 to 15 and select a chunk.")
@selection
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
    as_json: bool,
) -> None:
    if local:
        if not (0 <= x < 16 and 0 <= z < 16):
            raise click.UsageError("Local x/z must be 0..15")

        region, chunk = selected(source, index, position)

    else:
        if index is not None or position is not None:
            raise click.UsageError("World coordinates already select a chunk. Use --local with --index or --chunk")

        cx, x = divmod(x, 16)
        cz, z = divmod(z, 16)
        region, chunk = selected(source, None, (cx, cz))

    terrain = Terrain.from_chunk(chunk)
    if terrain is None:
        print_json(inspect.overview(region, chunk))
        return

    block = terrain.block((x, y, z), chunk)
    catalog = catalog_from()
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


@mapcache.command("records", help="Read records and show any remaining bytes.")
@click.argument("source", type=REGION)
@selection
@click.option("--record", type=click.IntRange(min=0), help="Inspect one record and its raw bytes.")
@click.option("--limit", type=click.IntRange(min=1), default=20, show_default=True)
@json_option
@io_errors
def records_command(
    source: Path,
    index: int | None,
    position: tuple[int, int] | None,
    record: int | None,
    limit: int,
    as_json: bool,
) -> None:
    region, chunk = selected(source, index, position)
    catalog = catalog_from()

    try:
        value = inspect.record_view(region, chunk, record, limit, catalog)

    except IndexError:
        raise click.UsageError("That record does not exist or is incomplete") from None

    if value is None:
        print_json(inspect.overview(region, chunk))
        return

    if as_json or record is not None:
        print_json(value)
        return

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


@mapcache.command("objects", help="Read object fields and transforms, and match definitions .")
@click.argument("source", type=REGION)
@selection
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
    as_json: bool,
) -> None:
    region, chunk = selected(source, index, position)
    catalog = catalog_from()
    try:
        value = inspect.object_view(region, chunk, item, limit, catalog)

    except IndexError:
        raise click.UsageError("That object item does not exist") from None

    if value is None:
        print_json(inspect.overview(region, chunk))
        return

    if as_json or item is not None:
        print_json(value)
        return

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


@mapcache.command("dump", help="Write chunk frames, terrain data, plane data, and source details.")
@click.argument("source", type=REGION)
@selection
@click.option("-o", "--output", type=OUTPUT, required=True, help="Empty output directory for this chunk.")
@json_option
@io_errors
def dump_command(
    source: Path, index: int | None, position: tuple[int, int] | None, output: Path, as_json: bool
) -> None:
    region, chunk = selected(source, index, position)
    value = inspect.dump(region, chunk, output)

    if as_json:
        print_json(value)
        return

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


@mapcache.command("census", help="Write block state, biome, record, and object statistics to JSON.")
@click.argument("source", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "census", show_default=True)
@click.option("--details", is_flag=True, help="Also write metadata for each chunk to JSONL.")
@json_option
@io_errors
def census_command(source: Path, output: Path, details: bool, as_json: bool) -> None:
    require_source(source)
    value = census.run(source, output, details=details, catalog=catalog_from(), version=_version())

    if as_json:
        print_json(value.totals)
        return

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


@mapcache.command("compare", help="Compare payload hashes and UUIDs for maps with the same name.")
@click.argument("before", type=SOURCE)
@click.argument("after", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "compare", show_default=True)
@io_errors
def compare_command(before: Path, after: Path, output: Path) -> None:
    require_source(before)
    require_source(after)
    print_json(compare.run(before, after, output, version=_version()))


@mapcache.command("map", help="Write height and block-state PNGs plus surface arrays for each map.")
@click.argument("source", type=SOURCE)
@click.option("-o", "--output", type=OUTPUT, default=REPORTS / "maps", show_default=True)
@click.option("--min-y", type=click.IntRange(0, 255), default=0, show_default=True)
@click.option("--max-y", type=click.IntRange(0, 255), default=255, show_default=True)
@click.option("--ignore-block", type=Number(4095), multiple=True, help="Full block IDs to skip.")
@click.option("--max-pixels", type=click.IntRange(min=256), default=16777216, show_default=True)
@io_errors
def map_command(
    source: Path, output: Path, min_y: int, max_y: int, ignore_block: tuple[int, ...], max_pixels: int
) -> None:
    require_source(source)

    if min_y > max_y:
        raise click.UsageError("--min-y must not exceed --max-y")

    for value in maps.run(source, output, min_y, max_y, ignore_block, max_pixels, version=_version()):
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


def _object_type_from_id(object_id: str, catalog: Catalog | None, version: int) -> int:
    if catalog is None or not catalog.registry_complete:
        raise click.UsageError("The object catalog is incomplete")

    definition = next((row for row in catalog.objects if row.object_id == object_id), None)

    if definition is None:
        raise click.UsageError(f"Unknown object ID: {object_id}")

    return definition.hash64 if version >= 7 else definition.network_id_candidate


@dataclass(frozen=True)
class SearchResult:
    matches: int
    limit_reached: bool
    notes: list[Diagnostic]


@mapcache.command("find", help="Write matching items as JSONL with typed data and source offsets.")
@click.argument("source", type=SOURCE)
@click.option("--state", type=Number(65535))
@click.option("--block-id", type=Number(4095))
@click.option("--record-type", type=click.IntRange(-128, 127))
@click.option("--object-type", type=Number(2**64 - 1))
@click.option("--object-id", help="Object definition ID .")
@click.option("--text", help="Find literal UTF-8 text in raw object items.")
@click.option("--limit", type=click.IntRange(min=1), default=100, show_default=True)
@click.option("-o", "--output", type=click.Path(path_type=Path, dir_okay=False))
@io_errors
def find_command(
    source: Path,
    state: int | None,
    block_id: int | None,
    record_type: int | None,
    object_type: int | None,
    object_id: str | None,
    text: str | None,
    limit: int,
    output: Path | None,
) -> None:
    catalog = catalog_from()
    if object_id is not None:
        if object_type is not None:
            raise click.UsageError("Use --object-id or --object-type, not both")
        object_type = _object_type_from_id(object_id, catalog, _version() or max(SUPPORTED_VERSIONS))

    if all(value is None for value in (state, block_id, record_type, object_type, text)):
        raise click.UsageError("Specify a state, block ID, record type, object type, or text")

    require_source(source)

    if output is not None and output.resolve() in (path.resolve() for path in paths(source)):
        raise click.UsageError("The output path must differ from the input files")

    query = search.Query(state, block_id, record_type, object_type, text.encode("utf-8") if text is not None else None)
    notes: list[Diagnostic] = list(catalog.notes) if catalog is not None else []

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)

    with click.open_file(str(output) if output is not None else "-", "w", encoding="utf-8") as stream:
        count = 0
        truncated = False

        for hit in islice(search.find(source, query, notes, catalog, version=_version()), limit + 1):
            if count == limit:
                truncated = True
                break

            stream.write(reports.line(hit) + "\n")
            count += 1

        stream.write(reports.line(SearchResult(count, truncated, notes)) + "\n")
