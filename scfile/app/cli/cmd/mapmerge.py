from pathlib import Path

import click

from scfile.app.cli import params
from scfile.app.cli.console import warn
from scfile.app.enums import CliCommand
from scfile.app.feedback import TaskFeedback
from scfile.app.tasks import execute
from scfile.app.tasks.mapmerge import MapMergeTask
from scfile.options import Options


@click.command(name=CliCommand.MAPMERGE)
@click.argument("SOURCE", type=params.MapMergeDir)
@click.argument("OUTPUT", type=params.MapMergeOutput)
def mapmerge(source: Path, output: Path) -> None:
    """Merge map tiles into a JPEG image."""

    if output.exists():
        warn(f"Output file will be replaced: {output}")

    feedback = TaskFeedback()
    summary = execute(MapMergeTask(source, output, Options()), feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)
