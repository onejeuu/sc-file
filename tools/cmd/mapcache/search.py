from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from . import scan
from .inspect import ObjectView, RecordDetails, object_details, record_details
from .mdat import records
from .mdat.models import Block, Location, RecordHeader, Slice
from .mdat.terrain import Terrain
from .metadata import Catalog
from .reports import Diagnostic


@dataclass(frozen=True)
class Query:
    state: int | None = None
    block_id: int | None = None
    record_type: int | None = None
    object_prefix: int | None = None
    text: bytes | None = None


@dataclass(frozen=True)
class UnknownRecord:
    header: RecordHeader
    remainder: Slice


@dataclass(frozen=True)
class Hit:
    location: Location
    kind: Literal["block", "record", "object", "record_tail"]
    data: Block | RecordDetails | ObjectView | UnknownRecord


def find(source: Path, query: Query, notes: list[Diagnostic], catalog: Catalog | None = None) -> Iterator[Hit]:
    for region, chunk in scan.chunks(source, notes):
        location = region.location(chunk.entry.index)
        terrain = Terrain.from_chunk(chunk)
        if terrain is not None:
            notes.extend(Diagnostic(region.path, chunk.entry.index, note) for note in terrain.notes)
            if query.state is not None or query.block_id is not None:
                for section in terrain.sections:
                    array = section.states()
                    if array is None:
                        continue
                    selected = np.ones(array.shape, dtype=bool)
                    if query.state is not None:
                        selected &= array == query.state
                    if query.block_id is not None:
                        selected &= (array & 0xFFF) == query.block_id
                    for y, z, x in np.argwhere(selected).tolist():
                        yield Hit(location, "block", terrain.block((x, section.y * 16 + y, z), chunk))
            if query.record_type is not None:
                data = records.read(terrain.records)
                notes.extend(Diagnostic(region.path, chunk.entry.index, note) for note in data.notes)
                for record in data.items:
                    if record.header.type == query.record_type:
                        yield Hit(location, "record", record_details(record, chunk, terrain, catalog))
                if data.stopped is not None and data.stopped.type == query.record_type:
                    yield Hit(location, "record_tail", UnknownRecord(data.stopped, data.tail))
        if query.object_prefix is not None or query.text is not None:
            items = scan.object_items(chunk)
            if items is None:
                continue
            notes.extend(Diagnostic(region.path, chunk.entry.index, note) for note in items.notes)
            for item in items.items:
                if query.object_prefix is not None and item.prefix != query.object_prefix:
                    continue
                if query.text is not None and query.text not in item.raw.data.tobytes():
                    continue
                yield Hit(location, "object", object_details(item, catalog))
