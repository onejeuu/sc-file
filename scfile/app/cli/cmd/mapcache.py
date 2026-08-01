import click
from rich import print

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.messages import task_message
from scfile.app.tasks import Context, Progress
from scfile.app.tasks.mapcache import Job
from scfile.enums import CliCommand, L
from scfile.options import HandlerOptions

from . import scfile


def _report(event: object) -> None:
    if isinstance(event, Progress) and event.completed == 0 and event.total is not None:
        print(L.INFO, f"Found {event.total} unique regions")
        print(L.INFO, "Starting merge...")
        return
    task_message(event)


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

    options = HandlerOptions(raw_blocks=raw)
    Job(source, output, options, workers).run(Context(report=_report))
