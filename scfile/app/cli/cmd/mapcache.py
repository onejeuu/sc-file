import click

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.messages import TaskFeedback, warning
from scfile.app.tasks import Context
from scfile.app.tasks.mapcache import Job
from scfile.enums import CliCommand
from scfile.options import HandlerOptions

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
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the result of every processed region.",
)
def mapcache_command(
    source: types.Path,
    output: types.Output,
    workers: int | None,
    raw: bool,
    verbose: bool,
) -> None:
    warning(
        "MDAT decoder is experimental. Blocks representation is not accurate. "
        "Full compatibility is unlikely."
    )

    options = HandlerOptions(raw_blocks=raw)
    feedback = TaskFeedback(verbose)
    summary = Job(source, output, options, workers).run(Context(report=feedback))
    feedback.finish(summary)
