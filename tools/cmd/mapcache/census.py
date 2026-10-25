from collections import Counter
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from scfile.formats.mca.mapping import BLOCKS_MAPPING

from . import scan
from .mdat import objects, records
from .mdat.models import XYZ, Location, State
from .mdat.objects import Instance
from .mdat.terrain import Terrain
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
    network_id: int
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
    object_prefixes: list[Count] = field(default_factory=list)
    object_sizes: list[Count] = field(default_factory=list)
    object_definitions: list[ObjectCount] = field(default_factory=list)
    object_flags: list[Count] = field(default_factory=list)
    metadata_notes: list[Diagnostic] = field(default_factory=list)
    notes: list[Diagnostic] = field(default_factory=list)


def counts(values: Counter[int]) -> list[Count]:
    return [Count(value, count) for value, count in sorted(values.items())]


def run(source: Path, output: Path, *, details: bool = False, catalog: Catalog | None = None) -> Census:
    result = Census(source.resolve())
    result.metadata_notes = catalog.notes if catalog is not None else []
    states: dict[int, StateCount] = {}
    biomes: Counter[int] = Counter()
    types: Counter[int] = Counter()
    flags: Counter[tuple[int, int]] = Counter()
    record_states: Counter[tuple[int, int | None]] = Counter()
    prefixes: Counter[int] = Counter()
    sizes: Counter[int] = Counter()
    object_flags: Counter[int] = Counter()
    definitions: dict[int, ObjectCount] = {}
    with ExitStack() as stack:
        region_writer = stack.enter_context(Writer(output / "regions.jsonl"))
        chunk_writer = stack.enter_context(Writer(output / "chunks.jsonl")) if details else None
        for region in scan.regions(source, result.notes):
            result.totals.regions += 1
            region_writer.write(region_info(region))
            for entry in region.entries:
                if not entry.present:
                    continue
                chunk = region.chunk(entry.index)
                location = region.location(entry.index)
                result.totals.chunks += 1
                notes = list(chunk.notes)
                terrain = Terrain.from_chunk(chunk)
                arrays = {}
                if terrain is not None:
                    result.totals.terrain_read += 1
                    notes.extend(terrain.notes)
                    seen = set()
                    for section in terrain.sections:
                        array = section.states()
                        if array is None:
                            continue
                        arrays[section.y] = array
                        ids, frequencies = np.unique(array, return_counts=True)
                        result.totals.stored_voxels += array.size
                        for value, frequency in zip(ids.tolist(), frequencies.tolist()):
                            state = State(value)
                            if value not in states:
                                vy, vz, vx = map(int, np.argwhere(array == value)[0])
                                states[value] = StateCount(
                                    state,
                                    0,
                                    0,
                                    location,
                                    (vx, section.y * 16 + vy, vz),
                                    BLOCKS_MAPPING[value & 255],
                                    catalog.block(state) if catalog is not None else None,
                                )
                            states[value].count += frequency
                            seen.add(value)
                            result.projection.voxels_with_additions += frequency if state.addition else 0
                            result.projection.voxels_with_metadata += frequency if state.metadata else 0
                            result.projection.metadata_on_air += (
                                frequency if state.block_id == 0 and state.metadata else 0
                            )
                            result.projection.nonair_to_air += (
                                frequency if state.block_id and BLOCKS_MAPPING[value & 255] == 0 else 0
                            )
                    for value in seen:
                        states[value].chunks += 1
                    biomes.update(terrain.biomes.data)
                    container = records.read(terrain.records)
                    notes.extend(container.notes)
                    result.totals.records += len(container.items)
                    for record in container.items:
                        kind = record.header.type
                        types[kind] += 1
                        flags[kind, record.payload.flags] += 1
                        state_value = None
                        if chunk.coordinates is not None:
                            cx, cz = chunk.coordinates
                            x, y, z = record.header.position
                            x, z = x - cx * 16, z - cz * 16
                            array = arrays.get(y // 16)
                            if array is not None and 0 <= x < 16 and 0 <= z < 16:
                                state_value = int(array[y % 16, z, x])
                        record_states[kind, state_value] += 1
                items = scan.object_items(chunk)
                if items is not None:
                    result.totals.objects_read += 1
                    result.totals.objects += len(items.items)
                    result.totals.empty_objects_chunks += chunk.objects_size == 0
                    notes.extend(items.notes)
                    for item in items.items:
                        sizes[item.raw.size] += 1
                        if item.prefix is not None:
                            prefixes[item.prefix] += 1
                            definition = catalog.object(item.prefix) if catalog is not None else None
                            instance = objects.instance(item, definition.behaviour if definition else None)
                            notes.extend(instance.notes)
                            result.totals.instances_read += instance.appearance is not None and instance.tail.size == 0
                            result.totals.instance_unparsed_bytes += instance.tail.size
                            if instance.header is not None:
                                object_flags[instance.header.flags] += 1
                            if item.prefix not in definitions:
                                definitions[item.prefix] = ObjectCount(
                                    item.prefix, 0, definition, location, item.index, instance
                                )
                            definitions[item.prefix].count += 1
                result.notes.extend(Diagnostic(region.path, entry.index, note) for note in notes)
                if chunk_writer is not None:
                    chunk_writer.write(chunk_info(region, chunk))
    result.states = [row for _, row in sorted(states.items())]
    result.biomes = counts(biomes)
    result.record_types = counts(types)
    result.record_flags = [RecordFlagCount(kind, flag, count) for (kind, flag), count in sorted(flags.items())]
    result.record_states = [
        RecordStateCount(kind, State(state) if state is not None else None, count)
        for (kind, state), count in sorted(
            record_states.items(), key=lambda item: (item[0][0], item[0][1] if item[0][1] is not None else -1)
        )
    ]
    result.object_prefixes = counts(prefixes)
    result.object_sizes = counts(sizes)
    result.object_definitions = [row for _, row in sorted(definitions.items())]
    result.object_flags = counts(object_flags)
    write(output / "census.json", result)
    return result
