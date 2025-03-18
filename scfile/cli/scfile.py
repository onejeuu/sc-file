import sys
from collections import defaultdict
from typing import Optional, Sequence, TypeAlias

import click
from rich import print

from scfile import convert
from scfile.cli.enums import Prefix
from scfile.consts import CLI
from scfile.convert.auto import MODELS_WITHOUT_SKELETON, ModelFormats
from scfile.core.context import ModelOptions
from scfile.core.context.options import ImageOptions, TextureOptions
from scfile.exceptions.base import ScFileException

from . import types
from .excepthook import excepthook


sys.excepthook = excepthook

FilesType: TypeAlias = Sequence[types.PathType]
FilesMap: TypeAlias = dict[types.PathType, list[types.PathType]]


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
    "--hdri",
    help="Parse textures as hdri (cubemaps).",
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
    paths: FilesType,
    output: Optional[types.PathType],
    model_formats: ModelFormats,
    skeleton: bool,
    hdri: bool,
    relative: bool,
    no_overwrite: bool,
):
    # In case program executed without arguments
    if not paths:
        no_args(ctx)
        return

    # Relative flag is useless without output path
    if not output and relative:
        print(Prefix.WARN, "[b]--relative[/] flag cannot be used without specifying [b]--output[/] option.")

    # Warn when any specified model format not supports skeletal animation
    if skeleton and has_no_skeleton_formats(model_formats):
        target_formats = filter_no_skeleton_formats(model_formats)
        print(Prefix.WARN, f"specified formats [b]({target_formats})[/] does not support skeleton and animation.")

    # Maps directories to their supported files, using directory as key
    files_map = paths_to_files_map(paths)
    if not files_map:
        print(Prefix.ERROR, "No supported files found in provided arguments.")
        print(CLI.FORMATS)
        return

    # Prepare options
    model_options = ModelOptions(parse_skeleton=skeleton)
    texture_options = TextureOptions(is_hdri=hdri)
    image_options = ImageOptions()
    overwrite = not no_overwrite

    # Iterates over each directory and its list of source files
    for root, sources in files_map.items():
        for source in sources:
            dest = output

            # Set relative path if enabled
            if output and relative:
                dest = output / source.relative_to(root.parent).parent

            # Convert file
            try:
                convert.auto(source, dest, model_options, texture_options, image_options, model_formats, overwrite)
                print(Prefix.INFO, f"File '{source.name}' converted to '{dest or source.parent}'")

            except ScFileException as err:
                print(Prefix.ERROR, str(err))


def has_no_skeleton_formats(model_formats: ModelFormats):
    """Checks if any model format in the list does not support skeletal animation."""
    return any(model in model_formats for model in MODELS_WITHOUT_SKELETON)


def filter_no_skeleton_formats(model_formats: ModelFormats):
    """Returns string of model formats that do not support skeletal animation."""
    return ", ".join(filter(lambda model: model in MODELS_WITHOUT_SKELETON, model_formats))


def no_args(ctx: click.Context) -> None:
    print("[b yellow]No arguments provided. Showing help:[/]\n")
    click.echo(f"{ctx.get_help()}")
    click.pause(CLI.PAUSE_TEXT)


def filter_files(files: FilesType):
    return list(filter(lambda path: path.is_file() and convert.is_supported(path), files))


def paths_to_files_map(paths: FilesType) -> FilesMap:
    files_map: FilesMap = defaultdict(list)
    resolved_symlinks: set[types.PathType] = set()

    for path in paths:
        if path.is_dir():
            if path.is_symlink():
                resolved = path.resolve()
                if resolved in resolved_symlinks:
                    continue
                resolved_symlinks.add(resolved)

            files_map[path].extend(filter_files(list(path.rglob("**/*"))))

        elif path.is_file():
            files_map[path.parent].extend(filter_files([path]))

    valid_files: FilesMap = {key: value for key, value in files_map.items() if value}
    return valid_files
