"""
CLI wrapper implementation.
"""

import sys
from typing import Optional

import click
import lz4.block
from rich import print

from scfile import convert
from scfile.cli.enums import Prefix
from scfile.consts import CLI, ModelFormats
from scfile.core.context import UserOptions
from scfile.exceptions.base import ScFileException

from . import types, utils
from .excepthook import excepthook


sys.excepthook = excepthook


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
    "--model-formats",
    help="Preferred format for models.",
    type=types.Formats,
    multiple=True,
)
@click.option(
    "--relative",
    help="Preserve sources relative directory structure in output (if specified).",
    is_flag=True,
)
@click.option(
    "--skeleton",
    help="Parse armature in models (if presented).",
    is_flag=True,
)
@click.option(
    "--animation",
    help="Parse animation in models (if presented).",
    is_flag=True,
)
@click.option(
    "--cubemap",
    help="Parse all input textures as cubemaps.",
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
    model_formats: ModelFormats,
    relative: bool,
    skeleton: bool,
    animation: bool,
    cubemap: bool,
    unique: bool,
):
    # In case program executed without arguments
    if not paths:
        utils.no_args(ctx)
        return

    # Relative flag is useless without output path
    if not output and relative:
        print(Prefix.WARN, "[b]--relative[/] flag cannot be used without specifying [b]--output[/] option.")

    # Animation flag is useless without skeleton
    if not skeleton and animation:
        skeleton = True

    # Warn if specified formats has unsupported features
    if model_formats:
        if skeleton:
            utils.check_unsupported_features(model_formats, CLI.NON_SKELETAL_FORMATS, "skeleton")

        if animation:
            utils.check_unsupported_features(model_formats, CLI.NON_ANIMATION_FORMATS, "animation")

    # Maps directories to their supported files, using directory as key
    files_map = utils.paths_to_files_map(paths)
    if not files_map:
        print(Prefix.ERROR, "No supported files found in provided arguments.")
        print(CLI.FORMATS)
        return

    # Prepare options
    options = UserOptions(
        model_formats=model_formats,
        parse_skeleton=skeleton,
        parse_animation=animation,
        overwrite=not unique,
    )

    # Iterate over each directory and its list of source files
    for root, sources in files_map.items():
        for source in sources:
            dest = output

            # Set relative path if enabled
            if output and relative:
                dest = output / source.relative_to(root.parent).parent

            # Convert source file
            try:
                convert.auto(source, dest, options, cubemap)

            except ScFileException as err:
                print(Prefix.ERROR, str(err))

            except lz4.block.LZ4BlockError as err:
                print(Prefix.ERROR, str(err))
                print(CLI.Text.HDRI_OFF if cubemap else CLI.Text.HDRI_ON)

            else:
                print(Prefix.INFO, f"File '{source.name}' converted to '{dest or source.parent}'")
