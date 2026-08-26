"""Map cache merging operations."""

import os
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import NamedTuple, Self

from scfile import exceptions, formats
from scfile.content import RegionContent
from scfile.options import Options

from . import paths


REGION_PREFIXES = ("reg.", "r.")
BACKUP = ".bck"

type Regions = dict[RegionKey, list[Path]]
type CancelCheck = Callable[[], bool] | None


class RegionKey(NamedTuple):
    """Map cache region coordinates."""

    x: int
    z: int

    @classmethod
    def parse(cls, stem: str) -> Self | None:
        """Parse region coordinates from filename."""

        for prefix in REGION_PREFIXES:
            stem = stem.removeprefix(prefix)

        try:
            x, z = map(int, stem.split("."))

        except ValueError:
            return None

        return cls(x, z)


class ScanResult(NamedTuple):
    """Map cache scan result."""

    paths: list[Path]
    errors: list[OSError]


class MergeResult(NamedTuple):
    """Map cache merge result."""

    filename: str
    chunks: int


def scan(
    source: Path,
    cancelled: CancelCheck = None,
) -> ScanResult:
    """Find valid map cache files."""

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
    """Group map cache paths by region coordinates."""

    grouped: Regions = defaultdict(list)

    for path in paths:
        if key := RegionKey.parse(path.stem):
            grouped[key].append(path)

    return dict(grouped)


def merge(
    key: RegionKey,
    sources: Iterable[Path],
    output: Path,
    options: Options,
    cancelled: CancelCheck = None,
) -> MergeResult:
    """
    Merge ``.mdat`` map cache into an ``.mca`` region file.

    Args:
        key: Region coordinates.
        sources: ``.mdat`` cache paths.
        output: Output directory.
        options (optional): Conversion options.
        cancelled (optional): Cancel check function.

    Returns:
        Output filename and the number of merged chunks.
    """

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
