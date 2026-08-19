from collections.abc import Callable

import click

from scfile import convert, types
from scfile.app.cli import params
from scfile.app.enums import AnimateCommand, CliCommand
from scfile.app.feedback import TaskFeedback
from scfile.app.tasks import execute
from scfile.app.tasks.animate import AnimateTask
from scfile.enums import FileFormat
from scfile.options import Options


@click.group(name=CliCommand.ANIMATE)
def animate() -> None:
    """Export model animations."""


def _execute(
    operation: Callable[..., types.ResultPath],
    source: types.SourcePath,
    models: tuple[types.SourcePath, ...],
    output: types.OutputLike,
    options: Options | None = None,
) -> None:
    output_path = convert.paths.destination(source, output, FileFormat.GLB.suffix)
    feedback = TaskFeedback()
    summary = execute(AnimateTask(operation, source, models, output_path, options or Options()), feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)


@animate.command(name=AnimateCommand.ARMS)
@click.argument(
    "ANIMATION",
    type=params.SourceFile,
)
@click.argument(
    "MODEL",
    type=params.SourceFile,
)
@click.argument(
    "HANDS",
    required=False,
    type=params.SourceFile,
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
    model: types.SourcePath,
    hands: types.SourcePath | None,
    output: types.OutputPath,
) -> None:
    """Apply first-person animation to weapon and hands models."""

    models = (model,) if hands is None else (model, hands)
    _execute(convert.animate.arms, animation, models, output)


@animate.command(name=AnimateCommand.FACE)
@click.argument(
    "ANIMATION",
    type=params.SourceFile,
)
@click.argument(
    "MODEL",
    type=params.SourceFile,
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

    _execute(convert.animate.face, animation, (model,), output)


@animate.command(name=AnimateCommand.BODY)
@click.argument(
    "ANIMATION",
    type=params.SourceFile,
)
@click.argument(
    "MODEL",
    type=params.SourceFile,
)
@click.option(
    "-O",
    "--output",
    required=False,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
@click.option(
    "--raw",
    is_flag=True,
    help="Keep technical animation clips.",
)
def body(
    animation: types.SourcePath,
    model: types.SourcePath,
    output: types.OutputPath,
    raw: bool,
) -> None:
    """Apply skeletal animation to a model."""

    _execute(convert.animate.body, animation, (model,), output, Options(raw_clips=raw))
