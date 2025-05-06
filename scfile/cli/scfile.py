import sys
from typing import Optional

import click
import lz4.block
from rich import print

from scfile import convert
from scfile.cli.enums import Prefix
from scfile.consts import CLI
from scfile.convert.auto import ModelFormats
from scfile.core.context import ModelOptions
from scfile.core.context.options import ImageOptions, TextureOptions
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
    "--tangents",
    help="Calculate normals from bi/tangents (if presented).",
    is_flag=True,
)
@click.option(
    "--hdri",
    help="Parse all input textures as cubemaps.",
    is_flag=True,
)
@click.option(
    "--relative",
    help="Preserve sources relative directory structure in output (if specified).",
    is_flag=True,
)
@click.option(
    "--no-overwrite",
    help="Do not overwrite an existing file.",
    is_flag=True,
)
@click.version_option(CLI.VERSION)
@click.pass_context
def scfile(
    ctx: click.Context,
    paths: types.FilesPaths,
    output: Optional[types.PathType],
    model_formats: ModelFormats,
    skeleton: bool,
    animation: bool,
    tangents: bool,
    hdri: bool,
    relative: bool,
    no_overwrite: bool,
):
    # In case program executed without arguments
    if not paths:
        utils.no_args(ctx)
        return

    # Relative flag is useless without output path
    if not output and relative:
        print(Prefix.WARN, "[b]--relative[/] flag cannot be used without specifying [b]--output[/] option.")

    # Warn when any specified model format not supports skeletal animation
    if skeleton and utils.has_no_skeleton_formats(model_formats):
        target_formats = utils.filter_no_skeleton_formats(model_formats)
        print(Prefix.WARN, f"specified formats [b]({target_formats})[/] doesn't support skeleton and animation.")

    # Maps directories to their supported files, using directory as key
    files_map = utils.paths_to_files_map(paths)
    if not files_map:
        print(Prefix.ERROR, "No supported files found in provided arguments.")
        print(CLI.FORMATS)
        return

    # Prepare options
    model_options = ModelOptions(parse_skeleton=skeleton, parse_animation=animation, calculate_tangents=tangents)
    texture_options = TextureOptions(is_hdri=hdri)
    image_options = ImageOptions()
    overwrite = not no_overwrite

    # Iterate over each directory and its list of source files
    for root, sources in files_map.items():
        for source in sources:
            dest = output

            # Set relative path if enabled
            if output and relative:
                dest = output / source.relative_to(root.parent).parent

            # Convert source file
            try:
                convert.auto(source, dest, model_options, texture_options, image_options, model_formats, overwrite)

            except ScFileException as err:
                print(Prefix.ERROR, str(err))

            except lz4.block.LZ4BlockError as err:
                print(Prefix.ERROR, str(err))
                print(CLI.Text.HDRI_OFF if hdri else CLI.Text.HDRI_ON)

            else:
                print(Prefix.INFO, f"File '{source.name}' converted to '{dest or source.parent}'")
