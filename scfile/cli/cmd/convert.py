import traceback
from typing import Optional

import click
from rich import print

from scfile import convert, exceptions, types
from scfile.cli import params
from scfile.cli.messages import warn_unsupported_features
from scfile.consts import INVALID_INPUT_HINT
from scfile.enums import CliCommand, L
from scfile.options import OnConflict, Options
from scfile.utils import files

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
    multiple=True,
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
def convert_command(
    paths: types.FilesPaths,
    output: types.Output,
    mdlformat: Optional[types.Formats],
    relative: bool,
    parent: bool,
    skeleton: bool,
    animation: bool,
    on_conflict: OnConflict,
) -> None:
    # Normalize options
    model_formats = mdlformat or None
    relative = relative or parent

    if relative and not output:
        raise click.UsageError("--relative and --parent require --output.")

    # Prepare options
    options = Options(
        model_formats=model_formats,
        skeleton=skeleton,
        animation=animation,
        on_conflict=on_conflict,
    )

    if model_formats:
        warn_unsupported_features(model_formats, options)

    out = str(output) if output else None

    # Iterate over each directory to their supported files
    for entry in files.walk(paths, parent=parent):
        dest = files.destination(relpath=entry.relpath, relative=relative, output=out)

        # Convert source file
        try:
            convert.auto(source=entry.path, output=dest, options=options)
            print(L.DONE, f"'{entry.path}'")

        except exceptions.BinaryStructureError as err:
            print(L.ERROR, f"'{err.location or entry.path}': {err}", INVALID_INPUT_HINT)

        except exceptions.ScFileException as err:
            print(L.ERROR, f"'{err.location or entry.path}': {err}")

        except Exception as err:
            print(L.EXCEPTION, f"File '{entry.path}' {repr(err)}.", INVALID_INPUT_HINT)
            print(traceback.format_exc())
            print()
