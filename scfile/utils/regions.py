"""Region merging from scattered map cache files."""

import threading
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable, NamedTuple, Optional, TypeAlias

from scfile import Options, exceptions, formats
from scfile.core import RegionContent


RegionKey: TypeAlias = tuple[int, int]
RegionsMapping: TypeAlias = dict[RegionKey, list[Path]]
LogCallback: TypeAlias = Callable[[str], None]
CancelEvent: TypeAlias = Optional[threading.Event]


class MergeResult(NamedTuple):
    filename: str
    chunks: int


def resolve(source: Path) -> list[Path]:
    """Collect valid .mdat files from a directory."""
    return [path for path in source.rglob("*.mdat") if path.stat().st_size > 0 and ".bck" not in str(path)]


def merge(
    key: RegionKey,
    paths: list[Path],
    output: Path,
    options: Options,
    cancelled: CancelEvent,
) -> MergeResult:
    """Merge multiple map chunks into single region file."""

    merged = RegionContent()
    seen: set[int] = set()

    for path in paths:
        if cancelled and cancelled.is_set():
            raise exceptions.MergeInterrupted()

        try:
            with formats.mdat.MdatDecoder(path, options) as mdat:
                data = mdat.decode()

            for chunk in data.chunks:
                if chunk.index not in seen:
                    merged.chunks.append(chunk)
                    seen.add(chunk.index)

        except Exception:
            raise exceptions.RegionFileError(str(path))

    (rx, rz) = key
    merged.rx = rx
    merged.rz = rz
    filename = f"r.{rx}.{rz}.mca"
    target = output / filename

    if target.exists():
        backup = target.with_suffix(".mca.bck")
        if not backup.exists():
            target.rename(backup)

    with formats.mca.McaEncoder(data=merged, options=options) as mca:
        mca.encode()
        mca.save(target)

    return MergeResult(filename, len(merged.chunks))


def parse(paths: Iterable[Path]) -> RegionsMapping:
    """Group .mdat paths by region coordinates."""

    regions: RegionsMapping = defaultdict(list)

    for path in paths:
        try:
            rx, rz = map(int, path.stem.removeprefix("reg.").removeprefix("r.").split("."))
            regions[(rx, rz)].append(path)

        except ValueError:
            continue

    return regions
