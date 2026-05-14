import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeAlias

import click
from rich import print

from scfile import formats, types
from scfile.cli import params
from scfile.core.context.content import RegionContent
from scfile.core.context.options import UserOptions
from scfile.enums import CliCommand, L

from . import scfile


RegionKey: TypeAlias = tuple[int, int]
LogCallback = Callable[[str], None]


# TODO: refactor me
def merge(
    item: tuple[RegionKey, list[types.Path]],
    output: types.Path,
    options: UserOptions,
    on_done: LogCallback | None = None,
    on_error: LogCallback | None = None,
) -> None:
    _done = on_done or (lambda msg: print(L.DONE, msg))
    _error = on_error or (lambda msg: print(L.ERROR, msg))

    (rx, rz), paths = item

    merged = RegionContent()
    seen: set[int] = set()

    for path in paths:
        try:
            with formats.mdat.MdatDecoder(file=path, options=options) as mdat:
                region = mdat.decode()

            for chunk in region.chunks:
                if chunk.index not in seen:
                    merged.chunks.append(chunk)
                    seen.add(chunk.index)

        except Exception as err:
            _error(f"{path.name} - {err}")

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

    _done(f"{filename} merged {len(merged.chunks)} chunks")


# TODO: refactor me
@scfile.command(name=CliCommand.MAPCACHE)
@click.argument(
    "SOURCE",
    type=params.MapCacheDir,
    nargs=1,
)
@click.option(
    "-O",
    "--output",
    help="Output results directory.",
    type=params.Output,
)
@click.option(
    "-W",
    "--workers",
    type=int,
    default=None,
    help="Number of worker threads (default: CPU count)",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Raw blocks without lookup",
)
def mapcache_command(
    source: types.Path,
    output: types.Output,
    workers: int | None,
    raw: bool,
) -> None:
    print(
        L.WARN,
        "[b yellow]MDAT decoder is EXPERIMENTAL. Blocks representation is NOT accurate. "
        "Expect broken visuals up close. Full compatibility is unlikely.[/]",
    )

    if not output:
        output = source.with_name(f"{source.name}_mca")
        output.mkdir(parents=True, exist_ok=True)

    mdats = [path for path in source.rglob("*.mdat") if path.stat().st_size > 0 and ".bck" not in str(path)]
    if not mdats:
        print(L.ERROR, f"No MDAT files found in {source}")
        return

    regions: dict[RegionKey, list[types.Path]] = defaultdict(list)
    for path in mdats:
        rx, rz = map(int, path.stem.lstrip("reg.").split("."))
        regions[(rx, rz)].append(path)

    if not regions:
        print(L.ERROR, f"No valid regions found in {source}")
        return

    print(L.INFO, f"Found {len(regions)} unique regions")
    print(L.INFO, "Starting merge...")

    options = UserOptions(parse_region_raw=raw)

    if workers is not None and workers <= 0:
        for item in regions.items():
            merge(item, output, options)

    else:
        max_workers = (workers or os.cpu_count() or 4) * 2
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda item: merge(item, output, options), regions.items())
