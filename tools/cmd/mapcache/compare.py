from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from . import scan
from .mdat import objects
from .mdat.models import Location, Note
from .mdat.reader import decompress
from .reports import Diagnostic, Writer, write


@dataclass(frozen=True)
class ChunkRef:
    location: Location
    source_sha256: str
    terrain_sha256: str | None
    objects_sha256: str | None


@dataclass(frozen=True)
class ObjectRef:
    location: Location
    index: int
    offset: int
    size: int
    prefix: int | None
    raw_sha256: str
    placement_sha256: str
    tail_sha256: str


@dataclass(frozen=True)
class ChunkChange:
    before: list[ChunkRef]
    after: list[ChunkRef]
    terrain_equal: bool | None
    objects_equal: bool | None


@dataclass(frozen=True)
class ObjectChange:
    map: str
    uuid: UUID
    before: list[ObjectRef]
    after: list[ObjectRef]
    ambiguous: bool
    prefix_delta: int | None
    placement_equal: bool | None
    tail_equal: bool | None


@dataclass(frozen=True)
class PrefixDelta:
    delta: int
    count: int


@dataclass
class Comparison:
    before: Path
    after: Path
    shared_chunks: int = 0
    identical_terrain: int = 0
    shared_uuids: int = 0
    only_before: int = 0
    only_after: int = 0
    ambiguous_uuids: int = 0
    identical_placement: int = 0
    identical_tail: int = 0
    prefix_deltas: list[PrefixDelta] = field(default_factory=list)
    notes: list[Diagnostic] = field(default_factory=list)


type ChunkKey = tuple[str, tuple[int, int] | None, int]
type ObjectKey = tuple[str, UUID]


def collect(
    source: Path, notes: list[Diagnostic], version: int | None = None
) -> tuple[dict[ChunkKey, list[ChunkRef]], dict[ObjectKey, list[ObjectRef]]]:
    chunks: dict[ChunkKey, list[ChunkRef]] = defaultdict(list)
    items: dict[ObjectKey, list[ObjectRef]] = defaultdict(list)
    root = source.resolve() if source.is_dir() else source.resolve().parent

    for region in scan.regions(source, notes, version):
        map_name = region.path.parent.relative_to(root).as_posix()
        fingerprint = region.fingerprint

        for entry in region.entries:
            if not entry.present:
                continue

            chunk = region.chunk(entry.index)
            location = region.location(entry.index)
            terrain_data = decompress(chunk.terrain, chunk.notes) if chunk.terrain is not None else None
            objects_data = decompress(chunk.objects, chunk.notes) if chunk.objects is not None else None
            chunks[map_name, region.coordinates, entry.index].append(
                ChunkRef(
                    location,
                    fingerprint,
                    sha256(terrain_data).hexdigest() if terrain_data is not None else None,
                    sha256(objects_data).hexdigest() if objects_data is not None else None,
                )
            )
            data = scan.object_items(chunk)
            notes.extend(Diagnostic(region.path, entry.index, note) for note in chunk.notes)

            if data is None:
                continue

            notes.extend(Diagnostic(region.path, entry.index, note) for note in data.notes)

            for item in data.items:
                placement = objects.placement(item)
                if placement is None:
                    notes.append(
                        Diagnostic(
                            region.path,
                            entry.index,
                            Note("objects", item.raw.offset, f"Placement is unavailable for item {item.index}"),
                        )
                    )
                    continue

                items[map_name, placement.uuid].append(
                    ObjectRef(
                        location,
                        item.index,
                        item.raw.offset,
                        item.raw.size,
                        item.prefix,
                        sha256(item.raw.data).hexdigest(),
                        sha256(placement.raw.data).hexdigest(),
                        sha256(placement.tail.data).hexdigest(),
                    )
                )

    return chunks, items


def equal(before: str | None, after: str | None) -> bool | None:
    return before == after if before is not None and after is not None else None


def run(before: Path, after: Path, output: Path, version: int | None = None) -> Comparison:
    result = Comparison(before.resolve(), after.resolve())
    old_chunks, old_items = collect(before, result.notes, version)
    new_chunks, new_items = collect(after, result.notes, version)
    deltas: Counter[int] = Counter()

    with Writer(output / "chunks.jsonl") as stream:
        for key in sorted(old_chunks.keys() | new_chunks.keys(), key=str):
            a, b = old_chunks.get(key, []), new_chunks.get(key, [])
            terrain_same = objects_same = None

            if len(a) == len(b) == 1:
                terrain_same = equal(a[0].terrain_sha256, b[0].terrain_sha256)
                objects_same = equal(a[0].objects_sha256, b[0].objects_sha256)
                result.shared_chunks += 1
                result.identical_terrain += terrain_same is True

            stream.write(ChunkChange(a, b, terrain_same, objects_same))

    with Writer(output / "objects.jsonl") as stream:
        for name, uuid in sorted(old_items.keys() | new_items.keys()):
            a, b = old_items.get((name, uuid), []), new_items.get((name, uuid), [])
            ambiguous = len(a) > 1 or len(b) > 1
            result.shared_uuids += bool(a and b)
            result.only_before += bool(a and not b)
            result.only_after += bool(b and not a)
            result.ambiguous_uuids += ambiguous
            delta = placement_same = tail_same = None

            if len(a) == len(b) == 1:
                old_prefix, new_prefix = a[0].prefix, b[0].prefix
                if old_prefix is not None and new_prefix is not None:
                    delta = new_prefix - old_prefix
                    deltas[delta] += 1
                placement_same = a[0].placement_sha256 == b[0].placement_sha256
                tail_same = a[0].tail_sha256 == b[0].tail_sha256
                result.identical_placement += placement_same
                result.identical_tail += tail_same

            stream.write(ObjectChange(name, uuid, a, b, ambiguous, delta, placement_same, tail_same))

    result.prefix_deltas = [PrefixDelta(delta, count) for delta, count in sorted(deltas.items())]
    write(output / "comparison.json", result)
    return result
