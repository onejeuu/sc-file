"""Map cache merging operations."""

import os
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import NamedTuple

from scfile import exceptions, formats
from scfile.content import RegionContent
from scfile.options import Options

from . import paths


type RegionKey = tuple[int, int]
type Regions = dict[RegionKey, list[Path]]
type CancelCheck = Callable[[], bool] | None

REGION_PREFIXES = ("reg.", "r.")
BACKUP = ".bck"


class ScanResult(NamedTuple):
    paths: list[Path]
    errors: list[OSError]


class MergeResult(NamedTuple):
    filename: str
    chunks: int


def scan(
    source: Path,
    cancelled: CancelCheck = None,
) -> ScanResult:
    """Find non empty mapcache files."""

    decoder = formats.MdatDecoder
    files: list[Path] = []
    errors: list[OSError] = []

    for root, _, names in os.walk(source, onerror=errors.append):
        if cancelled and cancelled():
            break

        for name in names:
            if cancelled and cancelled():
                break

            path = Path(root, name)
            if path.suffix != decoder.suffix() or BACKUP in path.suffixes:
                continue

            try:
                if path.stat().st_size:
                    files.append(path)

            except OSError as error:
                errors.append(error)

    return ScanResult(sorted(files), errors)


def group(
    paths: Iterable[Path],
) -> Regions:
    """Group mapcache paths by region coordinates."""

    grouped: Regions = defaultdict(list)

    for path in paths:
        key = _region_key(path)
        if key is not None:
            grouped[key].append(path)

    return dict(grouped)


def merge(
    key: RegionKey,
    sources: Iterable[Path],
    output: Path,
    options: Options,
    cancelled: CancelCheck = None,
) -> MergeResult:
    """Merge mapcache chunks into minecraft region."""

    decoder = formats.MdatDecoder
    encoder = formats.McaEncoder
    region = RegionContent()
    seen: set[int] = set()

    for source in sources:
        if cancelled and cancelled():
            raise exceptions.MergeInterrupted()

        try:
            with decoder(source, options) as mdat:
                data = mdat.decode()

        except exceptions.ScFileException:
            raise

        for chunk in data.chunks:
            if chunk.index not in seen:
                region.chunks.append(chunk)
                seen.add(chunk.index)

    region.rx, region.rz = key
    filename = f"r.{region.rx}.{region.rz}{encoder.suffix()}"
    target = output / filename

    with paths.stage(target) as temporary:
        with encoder(region, options) as mca:
            mca.encode()
            mca.save(temporary, close=False)

        if target.exists():
            backup = target.with_suffix(f"{encoder.suffix()}{BACKUP}")
            if not backup.exists():
                target.rename(backup)

    return MergeResult(filename, len(region.chunks))


def _region_key(
    path: Path,
) -> RegionKey | None:
    try:
        stem = path.stem
        for prefix in REGION_PREFIXES:
            if stem.startswith(prefix):
                stem = stem.removeprefix(prefix)
                break

        rx, rz = map(int, stem.split("."))
        return rx, rz

    except ValueError:
        return None
