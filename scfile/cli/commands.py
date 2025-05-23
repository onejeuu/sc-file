"""
CLI wrapper implementation.
"""

import traceback
from typing import Optional

import click
from rich import print

from scfile import convert
from scfile.cli.enums import Prefix
from scfile.consts import CLI, Formats
from scfile.core.context import UserOptions
from scfile.exceptions.base import ScFileException
from scfile.exceptions.file import InvalidStructureError

from . import types, utils


@click.command(name="scfile", epilog=CLI.EPILOG)
@click.argument("PATHS", type=types.Files, nargs=-1)
@click.option(
    "-O",
    "--output",
    help="Output results directory.",
    type=types.Output,
)
@click.option(
    "-F",
    "--mdlformat",
    help="Preferred format for models.",
    type=types.Formats,
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
@click.version_option(CLI.VERSION)
@click.pass_context
def scfile(
    ctx: click.Context,
    paths: types.FilesPaths,
    output: Optional[types.PathType],
    mdlformat: Optional[Formats],
    relative: bool,
    parent: bool,
    skeleton: bool,
    animation: bool,
    unique: bool,
) -> None:
    # In case program executed without arguments
    if not paths:
        utils.no_args(ctx)
        return

    # Normalize options
    model_formats = mdlformat or None
    if parent: relative = True
    if animation: skeleton = True

    # Relative flag is useless without output path
    if relative and not output:
        print(Prefix.WARN, "Flag [b]--relative[/] requires [b]--output[/] option.")

    # Warn if specified formats has unsupported features
    if model_formats:
        if skeleton: utils.check_feature_unsupported(model_formats, CLI.NON_SKELETAL_FORMATS, "skeleton")
        if animation: utils.check_feature_unsupported(model_formats, CLI.NON_ANIMATION_FORMATS, "animation")

    # Prepare options
    options = UserOptions(
        model_formats=model_formats,
        parse_skeleton=skeleton,
        parse_animation=animation,
        overwrite=not unique,
    )

    # Iterate over each directory to their supported files
    for root, source in utils.paths_to_files_map(paths):
        # Get relative subdir from root
        subdir = source.relative_to(root.parent if parent else root).parent

        # Use subdir in output path if relative enabled and output specified
        dest = output / subdir if (relative and output) else output

        # Convert source file
        try:
            convert.auto(source=source, output=dest, options=options)

        except InvalidStructureError as err:
            print(Prefix.ERROR, str(err), CLI.EXCEPTION)

        except ScFileException as err:
            print(Prefix.ERROR, str(err))

        except Exception as err:
            traceback.print_exception(err)
            print(Prefix.EXCEPTION, f"File '{source.as_posix()}' {err}.", CLI.EXCEPTION)

        else:
            src_path = source.relative_to(root)
            dst_path = dest or source.parent
            print(Prefix.INFO, f"File '{src_path.as_posix()}' converted to '{dst_path.as_posix()}'.")
