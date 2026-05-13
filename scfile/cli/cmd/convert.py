import traceback
from typing import Optional

import click
from rich import print

from scfile import convert, exceptions, types
from scfile.cli import params
from scfile.consts import CLI, Formats
from scfile.core import UserOptions
from scfile.enums import CliCommand, L
from scfile.utils import files, version

from . import scfile


@scfile.command(name=CliCommand.CONVERT)
@click.argument("PATHS", type=params.Files, nargs=-1)
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
    "--unique",
    help="Ensure file saved with unique name, avoiding overwrites.",
    is_flag=True,
)
@click.option(
    "--version",
    help="Show the version and exit.",
    callback=version.callback,
    is_flag=True,
    is_eager=True,
    expose_value=False,
)
def convert_command(
    paths: types.FilesPaths,
    output: types.Output,
    mdlformat: Optional[Formats],
    relative: bool,
    parent: bool,
    skeleton: bool,
    animation: bool,
    unique: bool,
) -> None:
    # Normalize options
    model_formats = mdlformat or None
    if parent:
        relative = True
    if animation:
        skeleton = True

    # Relative flag is useless without output path
    if relative and not output:
        print(L.WARN, "Flag [b]--relative[/] requires [b]--output[/] option.")

    # Warn if specified formats has unsupported features
    if model_formats:
        if skeleton:
            files.check_feature_unsupported(model_formats, CLI.NON_SKELETAL_FORMATS, "skeleton")

        if animation:
            files.check_feature_unsupported(model_formats, CLI.NON_ANIMATION_FORMATS, "animation")

    # Prepare options
    options = UserOptions(
        model_formats=model_formats,
        parse_skeleton=skeleton,
        parse_animation=animation,
        overwrite=not unique,
    )

    # Iterate over each directory to their supported files
    for root, source in files.paths_to_files_map(paths):
        # Get destination path
        dest = files.output_to_destination(root, source, output, relative, parent)

        # Convert source file
        try:
            convert.auto(source=source, output=dest, options=options)

        except exceptions.InvalidStructureError as err:
            print(L.ERROR, str(err), CLI.EXCEPTION)

        except exceptions.ScFileException as err:
            print(L.ERROR, str(err))

        except Exception as err:
            traceback.print_exception(err)
            print(L.EXCEPTION, f"File '{source.as_posix()}' {err}.", CLI.EXCEPTION)

        else:
            src_path = source.relative_to(root)
            dst_path = dest or source.parent
            print(L.INFO, f"File '{src_path.as_posix()}' converted to '{dst_path.as_posix()}'.")
