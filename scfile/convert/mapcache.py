"""Map cache merging operations."""

import os
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

from scfile import exceptions, formats
from scfile.content import RegionContent
from scfile.options import Options

from . import paths
from .regions import CancelCheck, Region


PREFIX = "reg."
MCA_PREFIX = "r."
MCA_SUFFIX = ".mca"
BACKUP_SUFFIX = ".bck"

type Regions = dict[Region, list[Path]]


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
            if path.suffix != decoder.suffix() or BACKUP_SUFFIX in path.suffixes:
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
        if key := Region.parse(path.stem.removeprefix(PREFIX)):
            grouped[key].append(path)

    return dict(grouped)


def merge(
    key: Region,
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

    region.x, region.z = key
    filename = f"{MCA_PREFIX}{region.x}.{region.z}{MCA_SUFFIX}"
    target = output / filename

    with paths.stage(target) as temporary:
        with encoder(region, options) as mca:
            mca.encode()
            mca.save(temporary, close=False)

        if options.backup_regions and target.exists():
            backup_path = target.with_suffix(f"{MCA_SUFFIX}{BACKUP_SUFFIX}")
            if not backup_path.exists():
                target.rename(backup_path)

    return MergeResult(filename, len(region.chunks))
