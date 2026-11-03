from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from .mdat.models import XZ, Chunk, Note
from .mdat.reader import Region, coordinates, paths
from .mdat.terrain import Terrain
from .reports import Diagnostic, RegionInfo, region_info, write


class Status(IntEnum):
    UNCACHED = 0
    EMPTY = 1
    SURFACE = 2
    UNAVAILABLE = 3
    OVERLAP = 4


@dataclass
class Surface:
    origin: XZ
    states: NDArray[np.uint16]
    heights: NDArray[np.int16]
    status: NDArray[np.uint8]

    @classmethod
    def create(cls, origin: XZ, width: int, height: int) -> "Surface":
        return cls(
            origin,
            np.zeros((height, width), dtype=np.uint16),
            np.full((height, width), -1, dtype=np.int16),
            np.zeros((height, width), dtype=np.uint8),
        )

    def put(self, chunk: Chunk, minimum: int, maximum: int, ignore: tuple[int, ...]) -> None:
        if chunk.coordinates is None:
            return
        cx, cz = chunk.coordinates
        x, z = cx * 16 - self.origin[0], cz * 16 - self.origin[1]
        window = np.s_[z : z + 16, x : x + 16]
        if self.status[window].any():
            self.status[window] = Status.OVERLAP
            chunk.notes.append(Note("file", chunk.allocation.offset, "More than one entry covers this map cell"))
            return

        terrain = Terrain.from_chunk(chunk)
        if terrain is None:
            self.status[window] = Status.UNAVAILABLE
            return

        chunk.notes.extend(terrain.notes)
        local_states = np.zeros((16, 16), dtype=np.uint16)
        local_heights = np.full((16, 16), -1, dtype=np.int16)

        for section in reversed(terrain.sections):
            low, high = max(0, minimum - section.y * 16), min(16, maximum - section.y * 16 + 1)
            if low >= high:
                continue

            array = section.states()
            if array is None:
                self.status[window] = Status.UNAVAILABLE
                return

            array = array[low:high]
            nonair = (array & 0xFFF) != 0

            if ignore:
                nonair &= ~np.isin(array & 0xFFF, ignore)

            present = nonair.any(axis=0) & (local_heights == -1)
            ys = len(array) - 1 - nonair[::-1].argmax(axis=0)
            zs, xs = np.nonzero(present)
            local_states[zs, xs] = array[ys[zs, xs], zs, xs]
            local_heights[zs, xs] = section.y * 16 + low + ys[zs, xs]

        self.states[window] = local_states
        self.heights[window] = local_heights
        self.status[window] = np.where(local_heights >= 0, Status.SURFACE, Status.EMPTY)

    def save(self, output: Path) -> None:
        output.mkdir(parents=True, exist_ok=True)
        rgba = np.zeros((*self.states.shape, 4), dtype=np.uint8)
        selected = self.status == Status.SURFACE
        rgba[:, :, 0][selected] = 160 + (self.states[selected] >> 10)
        rgba[:, :, 1][selected] = ((self.states[selected] >> 5) & 31) * 4
        rgba[:, :, 2][selected] = 128 + (self.states[selected] & 31) * 4
        rgba[:, :, 3][selected] = 255
        rgba[self.status == Status.EMPTY] = (45, 45, 45, 255)
        rgba[self.status == Status.UNAVAILABLE] = (255, 160, 0, 255)
        rgba[self.status == Status.OVERLAP] = (0, 220, 255, 255)
        Image.fromarray(rgba).save(output / "state.png")
        height_image = np.zeros_like(rgba)
        height_image[:, :, :3] = np.maximum(self.heights, 0)[:, :, None]
        height_image[:, :, 3][selected] = 255
        Image.fromarray(height_image).save(output / "height.png")
        np.savez_compressed(
            output / "surface.npz",
            origin=np.array(self.origin, dtype=np.int64),
            states=self.states,
            heights=self.heights,
            status=self.status,
        )


@dataclass(frozen=True)
class StatusCount:
    status: str
    count: int


@dataclass(frozen=True)
class MapInfo:
    source: Path
    output: Path
    origin: XZ | None
    size: XZ | None
    y_range: XZ
    ignored_blocks: tuple[int, ...]
    sources: list[RegionInfo]
    rendered: bool
    counts: list[StatusCount]
    notes: list[Diagnostic]


def _render_map(
    folder: Path,
    inputs: list[Path],
    target: Path,
    minimum: int,
    maximum: int,
    ignore: tuple[int, ...],
    max_pixels: int,
    version: int | None,
) -> MapInfo:
    positions = [position for path in inputs if (position := coordinates(path)) is not None]
    notes: list[Diagnostic] = []
    sources: list[RegionInfo] = []
    origin = None
    size = None
    counts: list[StatusCount] = []
    rendered = False

    if not positions:
        notes.extend(
            Diagnostic(path, None, Note("file", 0, "Filename does not contain region coordinates")) for path in inputs
        )
    else:
        x0 = min(x for x, _ in positions) * 512
        z0 = min(z for _, z in positions) * 512
        width = (max(x for x, _ in positions) + 1) * 512 - x0
        height = (max(z for _, z in positions) + 1) * 512 - z0
        origin = (x0, z0)
        size = (width, height)

        if width * height > max_pixels:
            notes.append(Diagnostic(folder, None, Note("file", 0, f"Map size {width}x{height} exceeds --max-pixels")))
        else:
            surface = Surface.create(origin, width, height)
            for path in inputs:
                try:
                    region = Region(path, version)
                except OSError as error:
                    notes.append(Diagnostic(path, None, Note("file", 0, str(error))))
                    continue
                sources.append(region_info(region))
                notes.extend(Diagnostic(path, None, note) for note in region.notes)
                if region.coordinates is None:
                    notes.append(
                        Diagnostic(path, None, Note("file", 0, "Filename does not contain region coordinates"))
                    )
                    continue
                for entry in region.entries:
                    if not entry.present:
                        continue
                    chunk = region.chunk(entry.index)
                    surface.put(chunk, minimum, maximum, ignore)
                    notes.extend(Diagnostic(path, entry.index, note) for note in chunk.notes)
            surface.save(target)
            values = Counter(surface.status.ravel().tolist())
            counts = [StatusCount(status.name.lower(), values[status]) for status in Status]
            rendered = True

    return MapInfo(folder, target.resolve(), origin, size, (minimum, maximum), ignore, sources, rendered, counts, notes)


def run(
    source: Path,
    output: Path,
    minimum: int,
    maximum: int,
    ignore: tuple[int, ...],
    max_pixels: int,
    version: int | None = None,
) -> list[MapInfo]:
    groups: dict[Path, list[Path]] = defaultdict(list)
    for path in paths(source):
        groups[path.parent.resolve()].append(path.resolve())

    results: list[MapInfo] = []
    for folder, inputs in sorted(groups.items()):
        relative = (
            folder.relative_to(source.resolve())
            if source.is_dir() and folder != source.resolve()
            else Path(folder.name)
        )
        target = output / relative
        result = _render_map(folder, inputs, target, minimum, maximum, ignore, max_pixels, version)
        write(target / "map.json", result)
        results.append(result)

    write(output / "maps.json", results)
    return results
