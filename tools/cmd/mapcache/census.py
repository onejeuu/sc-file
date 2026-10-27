from collections import Counter
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from scfile.formats.mca.mapping import BLOCKS_MAPPING

from . import scan
from .mdat import objects, records
from .mdat.models import XYZ, Chunk, Location, Note
from .mdat.objects import Instance
from .mdat.terrain import State, Terrain
from .metadata import BlockDefinition, Catalog, ObjectDefinition
from .reports import Diagnostic, Writer, chunk_info, region_info, write


@dataclass
class Totals:
    regions: int = 0
    chunks: int = 0
    terrain_read: int = 0
    objects_read: int = 0
    stored_voxels: int = 0
    records: int = 0
    objects: int = 0
    empty_objects_chunks: int = 0
    instances_read: int = 0
    instance_unparsed_bytes: int = 0


@dataclass
class Projection:
    voxels_with_additions: int = 0
    voxels_with_metadata: int = 0
    metadata_on_air: int = 0
    nonair_to_air: int = 0


@dataclass
class StateCount:
    state: State
    count: int
    chunks: int
    example: Location
    local_block: XYZ
    current_mapped_byte: int
    definition: BlockDefinition | None = None


@dataclass(frozen=True)
class Count:
    value: int
    count: int


@dataclass(frozen=True)
class RecordStateCount:
    type: int
    state: State | None
    count: int


@dataclass(frozen=True)
class RecordFlagCount:
    type: int
    flags: int
    count: int


@dataclass
class ObjectCount:
    type_id: int
    count: int
    definition: ObjectDefinition | None
    example: Location
    item: int
    instance: Instance


@dataclass
class Census:
    source: Path
    totals: Totals = field(default_factory=Totals)
    projection: Projection = field(default_factory=Projection)
    states: list[StateCount] = field(default_factory=list)
    biomes: list[Count] = field(default_factory=list)
    record_types: list[Count] = field(default_factory=list)
    record_flags: list[RecordFlagCount] = field(default_factory=list)
    record_states: list[RecordStateCount] = field(default_factory=list)
    object_types: list[Count] = field(default_factory=list)
    object_sizes: list[Count] = field(default_factory=list)
    object_definitions: list[ObjectCount] = field(default_factory=list)
    object_flags: list[Count] = field(default_factory=list)
    metadata_notes: list[Diagnostic] = field(default_factory=list)
    notes: list[Diagnostic] = field(default_factory=list)


def counts(values: Counter[int]) -> list[Count]:
    return [Count(value, count) for value, count in sorted(values.items())]


class _Collector:
    def __init__(self, source: Path, catalog: Catalog | None):
        self.catalog = catalog
        self.result = Census(source.resolve())
        self.result.metadata_notes = catalog.notes if catalog is not None else []
        self.states: dict[int, StateCount] = {}
        self.biomes: Counter[int] = Counter()
        self.record_types: Counter[int] = Counter()
        self.record_flags: Counter[tuple[int, int]] = Counter()
        self.record_states: Counter[tuple[int, int | None]] = Counter()
        self.object_types: Counter[int] = Counter()
        self.object_sizes: Counter[int] = Counter()
        self.object_flags: Counter[int] = Counter()
        self.definitions: dict[int, ObjectCount] = {}

    def add_chunk(self, chunk: Chunk, location: Location) -> list[Note]:
        self.result.totals.chunks += 1
        notes = list(chunk.notes)
        terrain = Terrain.from_chunk(chunk)
        if terrain is not None:
            self._terrain(terrain, location, chunk, notes)
        self._objects(chunk, location, notes)
        return notes

    def _terrain(self, terrain: Terrain, location: Location, chunk: Chunk, notes: list[Note]) -> None:
        self.result.totals.terrain_read += 1
        notes.extend(terrain.notes)
        arrays = {}
        seen: set[int] = set()

        for section in terrain.sections:
            array = section.states()
            if array is None:
                continue

            arrays[section.y] = array
            values, indices, frequencies = np.unique(array, return_index=True, return_counts=True)
            self.result.totals.stored_voxels += array.size

            for value, index, frequency in zip(values.tolist(), indices.tolist(), frequencies.tolist()):
                state = State(value)
                if value not in self.states:
                    vy, vz, vx = np.unravel_index(index, array.shape)
                    self.states[value] = StateCount(
                        state,
                        0,
                        0,
                        location,
                        (int(vx), section.y * 16 + int(vy), int(vz)),
                        BLOCKS_MAPPING[value & 255],
                        self.catalog.block(state) if self.catalog is not None else None,
                    )

                self.states[value].count += frequency
                seen.add(value)

                self.result.projection.voxels_with_additions += frequency if state.addition else 0
                self.result.projection.voxels_with_metadata += frequency if state.metadata else 0
                self.result.projection.metadata_on_air += frequency if state.block_id == 0 and state.metadata else 0
                self.result.projection.nonair_to_air += (
                    frequency if state.block_id and BLOCKS_MAPPING[value & 255] == 0 else 0
                )

        for value in seen:
            self.states[value].chunks += 1

        self.biomes.update(terrain.biomes.data)
        self._records(terrain, chunk, arrays, notes)

    def _records(self, terrain: Terrain, chunk: Chunk, arrays: dict[int, np.ndarray], notes: list[Note]) -> None:
        container = records.read(terrain.records)
        notes.extend(container.notes)
        self.result.totals.records += len(container.items)

        for record in container.items:
            kind = record.header.type
            self.record_types[kind] += 1
            self.record_flags[kind, record.payload.flags] += 1
            state_value = None

            if chunk.coordinates is not None:
                cx, cz = chunk.coordinates
                x, y, z = record.header.position
                x, z = x - cx * 16, z - cz * 16
                array = arrays.get(y // 16)
                if array is not None and 0 <= x < 16 and 0 <= z < 16:
                    state_value = int(array[y % 16, z, x])

            self.record_states[kind, state_value] += 1

    def _objects(self, chunk: Chunk, location: Location, notes: list[Note]) -> None:
        items = scan.object_items(chunk)
        if items is None:
            return

        self.result.totals.objects_read += 1
        self.result.totals.objects += len(items.items)
        self.result.totals.empty_objects_chunks += chunk.objects_size == 0
        notes.extend(items.notes)

        for item in items.items:
            self.object_sizes[item.raw.size] += 1
            if item.type_id is None:
                continue

            type_id = item.type_id
            self.object_types[type_id] += 1
            definition = self.catalog.object(item.prefix) if self.catalog is not None else None
            instance = objects.instance(item, definition.behaviour if definition else None)
            notes.extend(instance.notes)
            self.result.totals.instances_read += instance.appearance is not None and instance.tail.size == 0
            self.result.totals.instance_unparsed_bytes += instance.tail.size

            if instance.header is not None:
                self.object_flags[instance.header.flags] += 1

            if type_id not in self.definitions:
                self.definitions[type_id] = ObjectCount(type_id, 0, definition, location, item.index, instance)

            self.definitions[type_id].count += 1

    def finish(self) -> Census:
        result = self.result
        result.states = [row for _, row in sorted(self.states.items())]
        result.biomes = counts(self.biomes)
        result.record_types = counts(self.record_types)
        result.record_flags = [
            RecordFlagCount(kind, flag, count) for (kind, flag), count in sorted(self.record_flags.items())
        ]
        result.record_states = [
            RecordStateCount(kind, State(state) if state is not None else None, count)
            for (kind, state), count in sorted(
                self.record_states.items(),
                key=lambda item: (item[0][0], item[0][1] if item[0][1] is not None else -1),
            )
        ]
        result.object_types = counts(self.object_types)
        result.object_sizes = counts(self.object_sizes)
        result.object_definitions = [row for _, row in sorted(self.definitions.items())]
        result.object_flags = counts(self.object_flags)
        return result


def run(
    source: Path,
    output: Path,
    *,
    details: bool = False,
    catalog: Catalog | None = None,
    version: int | None = None,
) -> Census:
    collector = _Collector(source, catalog)
    result = collector.result

    with ExitStack() as stack:
        region_writer = stack.enter_context(Writer(output / "regions.jsonl"))
        chunk_writer = stack.enter_context(Writer(output / "chunks.jsonl")) if details else None

        for region in scan.regions(source, result.notes, version):
            result.totals.regions += 1
            region_writer.write(region_info(region))

            for entry in region.entries:
                if not entry.present:
                    continue

                chunk = region.chunk(entry.index)
                notes = collector.add_chunk(chunk, region.location(entry.index))
                result.notes.extend(Diagnostic(region.path, entry.index, note) for note in notes)

                if chunk_writer is not None:
                    chunk_writer.write(chunk_info(region, chunk))

    collector.finish()
    write(output / "census.json", result)
    return result
