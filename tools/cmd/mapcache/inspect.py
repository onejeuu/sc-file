from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from . import carpenters, scan
from .carpenters import Carpenter
from .mdat import objects, records
from .mdat.models import Chunk, Slice, view
from .mdat.objects import Instance, ObjectItem
from .mdat.reader import Region, decompress
from .mdat.records import Record, RecordHeader
from .mdat.terrain import State, Terrain
from .metadata import Catalog, ObjectDefinition
from .reports import (
    ChunkInfo,
    ContainerInfo,
    Diagnostic,
    Range,
    RegionInfo,
    TerrainInfo,
    chunk_info,
    region_info,
    terrain_info,
    write,
)


@dataclass(frozen=True)
class Overview:
    chunk: ChunkInfo
    terrain: TerrainInfo | None
    records: ContainerInfo | None
    objects: ContainerInfo | None


@dataclass(frozen=True)
class ObjectView:
    item: ObjectItem
    definition: ObjectDefinition | None
    instance: Instance


@dataclass(frozen=True)
class RecordDetails:
    record: Record
    state: State | None
    carpenter: Carpenter


@dataclass(frozen=True)
class RecordView:
    chunk: ChunkInfo
    container: ContainerInfo
    items: list[RecordDetails]
    stopped: RecordHeader | None
    tail_preview: Slice
    metadata_notes: list[Diagnostic]


@dataclass(frozen=True)
class ObjectsView:
    chunk: ChunkInfo
    container: ContainerInfo
    items: list[ObjectView]
    tail_preview: Slice
    metadata_notes: list[Diagnostic]


@dataclass(frozen=True)
class Artifact:
    name: str
    size: int
    sha256: str


@dataclass(frozen=True)
class Dump:
    source: RegionInfo
    overview: Overview
    files: list[Artifact]


def preview(raw: Slice) -> Slice:
    return Slice(raw.offset, min(256, raw.size), raw.data[:256])


def overview(region: Region, chunk: Chunk) -> Overview:
    terrain = Terrain.from_chunk(chunk)
    record_info = None
    if terrain is not None:
        data = records.read(terrain.records)
        record_info = ContainerInfo(data.count, len(data.items), Range.of(data.tail), data.notes)

    data_objects = scan.object_items(chunk)
    object_info = (
        ContainerInfo(data_objects.count, len(data_objects.items), Range.of(data_objects.tail), data_objects.notes)
        if data_objects is not None
        else None
    )

    return Overview(
        chunk_info(region, chunk), terrain_info(terrain) if terrain is not None else None, record_info, object_info
    )


def record_details(record: Record, chunk: Chunk, terrain: Terrain, catalog: Catalog | None = None) -> RecordDetails:
    state = carpenters.state_at(record, chunk, terrain)
    return RecordDetails(record, state, carpenters.interpret(record, state, catalog))


def record_view(
    region: Region, chunk: Chunk, index: int | None, limit: int, catalog: Catalog | None = None
) -> RecordView | None:
    terrain = Terrain.from_chunk(chunk)
    if terrain is None:
        return None

    data = records.read(terrain.records)
    items = [data.items[index]] if index is not None else data.items[:limit]
    container = ContainerInfo(data.count, len(data.items), Range.of(data.tail), terrain.notes + data.notes)

    return RecordView(
        chunk_info(region, chunk),
        container,
        [record_details(item, chunk, terrain, catalog) for item in items],
        data.stopped,
        preview(data.tail),
        catalog.notes if catalog is not None else [],
    )


def object_details(item: ObjectItem, catalog: Catalog | None = None) -> ObjectView:
    definition = catalog.object(item.type_id) if catalog is not None else None
    return ObjectView(item, definition, objects.instance(item, definition.behaviour if definition else None))


def object_view(
    region: Region, chunk: Chunk, index: int | None, limit: int, catalog: Catalog | None = None
) -> ObjectsView | None:
    data = scan.object_items(chunk)
    if data is None:
        return None

    items = [data.items[index]] if index is not None else data.items[:limit]
    rows = [object_details(item, catalog) for item in items]

    return ObjectsView(
        chunk_info(region, chunk),
        ContainerInfo(
            data.count,
            len(data.items),
            Range.of(data.tail),
            data.notes + [note for row in rows for note in row.instance.notes],
        ),
        rows,
        preview(data.tail),
        catalog.notes if catalog is not None else [],
    )


def dump(region: Region, chunk: Chunk, output: Path) -> Dump:
    output.mkdir(parents=True, exist_ok=True)

    if any(output.iterdir()):
        raise FileExistsError(f"The dump output directory must be empty: {output}")

    artifacts: list[Artifact] = []

    def save(name: str, data: bytes | memoryview) -> None:
        (output / name).write_bytes(data)
        artifacts.append(Artifact(name, len(data), sha256(data).hexdigest()))

    save("entry.bin", chunk.entry.raw.data)
    save("allocation.bin", chunk.allocation.data)

    if chunk.header is not None:
        save("header.bin", chunk.header_raw.data)

    if chunk.terrain is not None:
        save("terrain.zst", chunk.terrain.raw.data)
        if chunk.terrain.data is not None:
            save("terrain.chunk", chunk.header_raw.data.tobytes() + chunk.terrain.data)

    terrain = Terrain.from_chunk(chunk)
    if terrain is not None:
        for name, raw in (
            ("blocks", terrain.blocks),
            ("metadata", terrain.metadata),
            ("lighting_0", terrain.lighting[0]),
            ("lighting_1", terrain.lighting[1]),
            ("lighting_2", terrain.lighting[2]),
            ("additions", terrain.additions),
            ("biomes", terrain.biomes),
            ("records", terrain.records),
        ):
            save(name + ".bin", raw.data)

    if chunk.objects is not None:
        decompress(chunk.objects, chunk.notes)
        size = view(region.raw, chunk.objects.raw.offset - 4, 4)
        save("objects-size.bin", size.data)
        save("objects.zst", chunk.objects.raw.data)
        if chunk.objects.data is not None:
            save("objects.objects", chunk.objects.data)

    result = Dump(region_info(region), overview(region, chunk), artifacts)
    write(output / "chunk.json", result)
    return result
