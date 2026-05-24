import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
from rich import print

from scfile import types
from scfile.cli import params
from scfile.core import Options
from scfile.enums import CliCommand, L
from scfile.utils import regions

from . import scfile


def _merge(key: regions.RegionKey, paths: list[Path], output: Path, options: Options):
    try:
        filename, chunks = regions.merge(key, paths, output, options)
        print(L.DONE, f"{filename} merged {chunks} chunks")

    except regions.RegionFileError as err:
        print(L.ERROR, repr(err))


@scfile.command(name=CliCommand.MAPCACHE)
@click.argument(
    "SOURCE",
    type=params.MapCacheDir,
    nargs=1,
    required=True,
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

    mdats = regions.resolve(source)
    if not mdats:
        print(L.ERROR, f"No MDAT files found in '{source}'")
        return

    mapping = regions.parse(mdats)

    if not mapping:
        print(L.ERROR, f"No valid regions found in '{source}'")
        return

    if not output:
        output = source.with_name(f"{source.name}_mca")
        output.mkdir(parents=True, exist_ok=True)

    print(L.INFO, f"Found {len(mapping)} unique regions")
    print(L.INFO, "Starting merge...")

    options = Options(chunks_raw=raw)

    if workers is not None and workers <= 0:
        for key, paths in mapping.items():
            _merge(key, paths, output, options)

    else:
        max_workers = (workers or os.cpu_count() or 4) * 2
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda key, paths: _merge(key, paths, output, options), mapping.items())
