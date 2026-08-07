from collections.abc import Callable
from pathlib import Path

import click

from scfile import convert, types
from scfile.app.cli import params
from scfile.app.cli.messages import TaskFeedback
from scfile.app.tasks import Context
from scfile.app.tasks.animation import Job
from scfile.enums import AnimateCommand, CliCommand, FileFormat

from . import scfile


@scfile.group(name=CliCommand.ANIMATE)
def animate() -> None:
    """Export models with external animations."""


def _execute(
    operation: Callable[..., Path],
    source: types.SourcePath,
    models: tuple[types.SourcePath, ...],
    output: types.OutputLike,
) -> None:
    output_path = convert.files.destination(source, output, FileFormat.GLB.suffix)
    feedback = TaskFeedback()
    summary = Job(operation, source, models, output_path).run(Context(report=feedback))
    feedback.finish(summary)

    if summary.failed:
        raise click.exceptions.Exit(1)


@animate.command(name=AnimateCommand.ARMS)
@click.argument(
    "ANIMATION",
    type=params.File,
)
@click.argument(
    "MODELS",
    nargs=-1,
    required=True,
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=False,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def arms(
    animation: types.SourcePath,
    models: tuple[types.SourcePath, ...],
    output: types.OutputPath,
) -> None:
    """Apply first-person animation to weapon and hands models."""

    _execute(convert.animation.arms, animation, models, output)


@animate.command(name=AnimateCommand.FACE)
@click.argument(
    "ANIMATION",
    type=params.File,
)
@click.argument(
    "MODEL",
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=False,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def face(
    animation: types.SourcePath,
    model: types.SourcePath,
    output: types.OutputPath,
) -> None:
    """Apply facial animation to a head model."""

    _execute(convert.animation.face, animation, (model,), output)


@animate.command(name=AnimateCommand.BODY)
@click.argument(
    "LIBRARY",
    type=params.File,
)
@click.argument(
    "MODEL",
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=False,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def body(
    library: types.SourcePath,
    model: types.SourcePath,
    output: types.OutputPath,
) -> None:
    """Apply animation library to a model."""

    _execute(convert.animation.body, library, (model,), output)
