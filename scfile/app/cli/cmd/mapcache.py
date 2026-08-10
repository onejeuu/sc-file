import click

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.feedback import TaskFeedback
from scfile.app.cli.console import warn
from scfile.app.enums import CliCommand
from scfile.app.tasks import execute
from scfile.app.tasks.mapcache import MapCacheTask
from scfile.options import Options

from . import scfile


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
    "--raw",
    is_flag=True,
    help="Raw blocks without lookup",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the result of every processed region.",
)
def mapcache_command(
    source: types.SourcePath,
    output: types.OutputPath,
    workers: int | None,
    raw: bool,
    verbose: bool,
) -> None:
    warn(
        "MDAT decoder is experimental. Blocks representation is not accurate. Full compatibility is unlikely."
    )

    options = Options(region={"raw_blocks": raw})
    feedback = TaskFeedback(verbose)
    summary = execute(MapCacheTask(source, output, options, workers), feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)
