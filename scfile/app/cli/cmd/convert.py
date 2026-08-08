import click

from scfile import types
from scfile.app.cli import params
from scfile.app.cli.messages import TaskFeedback, warn_unsupported_features
from scfile.app.tasks import Context
from scfile.app.tasks.convert import Job
from scfile.enums import CliCommand, FileFormat
from scfile.options import OnConflict, Options

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
    type=params.Output,
)
@click.option(
    "-F",
    "--mdlformat",
    help="Preferred format for models.",
    type=params.Formats,
)
@click.option(
    "--relative",
    help="Preserve directory structure from source in output.",
    is_flag=True,
)
@click.option(
    "--parent",
    help="Use parent directory as starting point in relative directory.",
    is_flag=True,
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
    mdlformat: FileFormat | None,
    relative: bool,
    parent: bool,
    skeleton: bool,
    animation: bool,
    workers: int | None,
    on_conflict: OnConflict,
    verbose: bool,
) -> None:
    # Normalize options
    relative = relative or parent

    if relative and not output:
        raise click.UsageError("--relative and --parent require --output.")

    # Prepare options
    options = Options(
        model={
            "skeleton": skeleton,
            "animation": animation,
        },
        model_format=mdlformat,
        on_conflict=on_conflict,
    )

    if mdlformat:
        warn_unsupported_features((mdlformat,), options.model)

    job = Job(
        sources=tuple(paths),
        whitelist=(),
        options=options,
        output=output,
        relative=relative,
        parent=parent,
        workers=workers,
    )
    feedback = TaskFeedback(verbose)
    summary = job.run(Context(report=feedback))
    feedback.finish(summary)

    if summary.failed:
        raise click.exceptions.Exit(1)
