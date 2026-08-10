import click

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.feedback import TaskFeedback
from scfile.app.cli.console import warn
from scfile.app.enums import CliCommand, OutputLayout
from scfile.app.tasks import execute
from scfile.app.tasks.convert import ConvertTask
from scfile.enums import FileFormat
from scfile.options import OnConflict, Options
from scfile.registry import REGISTRY

from . import scfile


@scfile.command(name=CliCommand.CONVERT)
@click.argument(
    "PATHS",
    type=params.Files,
    nargs=-1,
    required=True,
)
@click.option(
    "-O",
    "--output",
    help="Output results directory.",
    type=params.OutputDir,
)
@click.option(
    "-F",
    "--mdlformat",
    "--model-format",
    "model_format",
    help="Preferred output format for models.",
    type=params.ModelFormats,
)
@click.option(
    "-I",
    "--include",
    "formats",
    help="Process only these source formats. May be repeated.",
    type=params.InputFormats,
    multiple=True,
)
@click.option(
    "--layout",
    type=params.Layouts,
    default=OutputLayout.FLAT,
    show_default=OutputLayout.FLAT.value,
    help="Output layout: flat, relative to source, or with source root.",
)
@click.option(
    "--skeleton",
    help="Parse armature in models.",
    is_flag=True,
)
@click.option(
    "--animation",
    help="Parse builtin clips in models.",
    is_flag=True,
)
@click.option(
    "--on-conflict",
    type=params.OnConflict,
    default="overwrite",
    help="What to do when output file already exists.",
)
@click.option(
    "-W",
    "--workers",
    type=int,
    default=None,
    help="Number of worker threads (default: CPU count).",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the result of every processed file.",
)
def convert_command(
    paths: types.FilesPaths,
    output: types.OutputPath,
    model_format: FileFormat | None,
    formats: tuple[FileFormat, ...],
    layout: OutputLayout,
    skeleton: bool,
    animation: bool,
    workers: int | None,
    on_conflict: OnConflict,
    verbose: bool,
) -> None:
    if layout is not OutputLayout.FLAT and not output:
        raise click.UsageError("Non-flat --layout requires --output.")

    # Prepare options
    options = Options(
        model={"skeleton": skeleton, "animation": animation},
        model_format=model_format,
        on_conflict=on_conflict,
    )

    if model_format:
        unsupported = tuple(
            feature for feature in options.model.features if not REGISTRY.model_supports(model_format, feature)
        )
        if unsupported:
            features = ", ".join(unsupported)
            warn(
                f"Requested model feature is not supported by {model_format.upper()}: {features}."
            )

    task = ConvertTask(
        sources=tuple(paths),
        filters=tuple(REGISTRY.filters_for(*formats)),
        options=options,
        output=output,
        layout=layout,
        workers=workers,
    )
    feedback = TaskFeedback(verbose)
    summary = execute(task, feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)
