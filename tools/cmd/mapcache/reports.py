import json
import math
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any, Self
from uuid import UUID

from .mdat.models import Chunk, Entry, Frame, Header, Location, Note, Slice
from .mdat.reader import Region
from .mdat.terrain import State, Terrain


@dataclass(frozen=True)
class Range:
    offset: int
    size: int
    available: int

    @classmethod
    def of(cls, raw: Slice) -> Self:
        return cls(raw.offset, raw.size, len(raw.data))


@dataclass(frozen=True)
class FrameInfo:
    compressed: Range
    decompressed_size: int | None


@dataclass(frozen=True)
class ChunkInfo:
    location: Location
    entry: Entry
    uuid: UUID | None
    header: Header | None
    allocation: Range
    physical_size: int | None
    terrain: FrameInfo | None
    objects: FrameInfo | None
    notes: list[Note]


@dataclass(frozen=True)
class RegionInfo:
    path: Path
    coordinates: tuple[int, int] | None
    size: int
    sha256: str
    notes: list[Note]


@dataclass(frozen=True)
class PlaneInfo:
    name: str
    range: Range


@dataclass(frozen=True)
class TerrainInfo:
    sections: tuple[int, ...]
    additions: tuple[int, ...]
    planes: tuple[PlaneInfo, ...]
    notes: list[Note]


@dataclass(frozen=True)
class ContainerInfo:
    declared: int | None
    parsed: int
    tail: Range
    notes: list[Note]


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    index: int | None
    note: Note


def chunk_info(region: Region, chunk: Chunk) -> ChunkInfo:
    def frame_info(frame: Frame | None) -> FrameInfo | None:
        return (
            FrameInfo(Range.of(frame.raw), len(frame.data) if frame.data is not None else None)
            if frame is not None
            else None
        )

    return ChunkInfo(
        region.location(chunk.entry.index),
        chunk.entry,
        chunk.entry.uuid if chunk.entry.present else None,
        chunk.header,
        Range.of(chunk.allocation),
        chunk.physical_size,
        frame_info(chunk.terrain),
        frame_info(chunk.objects),
        chunk.notes,
    )


def region_info(region: Region) -> RegionInfo:
    return RegionInfo(region.path, region.coordinates, len(region.raw), region.fingerprint, region.notes)


def terrain_info(terrain: Terrain) -> TerrainInfo:
    planes = (
        ("blocks", terrain.blocks),
        ("metadata", terrain.metadata),
        ("lighting_0", terrain.lighting[0]),
        ("lighting_1", terrain.lighting[1]),
        ("lighting_2", terrain.lighting[2]),
        ("additions", terrain.additions),
        ("biomes", terrain.biomes),
        ("records", terrain.records),
    )

    return TerrainInfo(
        tuple(section.y for section in terrain.sections),
        tuple(y for y in range(16) if terrain.header.addition_mask & (1 << y)),
        tuple(PlaneInfo(name, Range.of(raw)) for name, raw in planes),
        terrain.notes,
    )


def encode(value: Any) -> Any:
    if isinstance(value, State):
        return {
            "value": value.value,
            "hex": f"0x{value.value:04x}",
            "block_id": value.block_id,
            "metadata": value.metadata,
            "addition": value.addition,
        }
    if isinstance(value, Slice):
        return {"offset": value.offset, "size": value.size, "available": len(value.data), "hex": value.data.hex()}
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: encode(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Path | UUID):
        return str(value)
    if isinstance(value, bytes | memoryview):
        return value.hex()
    if isinstance(value, tuple | list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def text(value: object) -> str:
    return json.dumps(encode(value), ensure_ascii=False, allow_nan=False, indent=2)


def line(value: object) -> str:
    return json.dumps(encode(value), ensure_ascii=False, allow_nan=False)


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text(value) + "\n", encoding="utf-8")


class Writer:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open("w", encoding="utf-8")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.file.close()

    def write(self, value: object) -> None:
        self.file.write(line(value) + "\n")
