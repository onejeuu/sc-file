from typing import cast

import click

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.console import warn
from scfile.app.enums import CliCommand
from scfile.app.feedback import TaskFeedback
from scfile.app.mapcache import supported_version_from_path, version_from_path
from scfile.app.tasks import execute
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.formats.mdat.versions import SUPPORTED_VERSIONS
from scfile.options import MdatVersion, Options


@click.command(name=CliCommand.MAPCACHE)
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
    type=params.OutputDir,
)
@click.option(
    "-W",
    "--workers",
    type=int,
    default=None,
    help="Number of worker threads (default: CPU count)",
)
@click.option(
    "--biomes/--no-biomes",
    default=True,
    help="Export biome data.",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Keep the original region before its first replacement.",
)
@click.option(
    "--version",
    type=click.Choice(tuple(str(version) for version in SUPPORTED_VERSIONS)),
    default=None,
    help="MDAT major version (default: latest).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the result of every processed region.",
)
def mapcache(
    source: types.SourcePath,
    output: types.OutputPath,
    workers: int | None,
    biomes: bool,
    backup: bool,
    version: str | None,
    verbose: bool,
) -> None:
    """Merge map cache regions."""

    detected = version_from_path(source)
    if detected is not None and supported_version_from_path(source) is None:
        selected = f"v{version}" if version is not None else "the latest supported version"
        warn(f"Unsupported MDAT version in path: {detected}. Using {selected}.")

    options = Options(
        biomes=biomes,
        backup_regions=backup,
        mdat_version=cast(MdatVersion, int(version)) if version is not None else supported_version_from_path(source),
    )
    feedback = TaskFeedback(verbose)
    summary = execute(MapCacheTask(source, output, options, workers), feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)
