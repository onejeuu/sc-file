import sys
from collections import defaultdict
from typing import Optional, Sequence, TypeAlias

import click
from rich import print

from scfile.cli.enums import Prefix
from scfile.consts import CLI
from scfile.core.meta import ModelOptions
from scfile.core.meta.options import ImageOptions, TextureOptions
from scfile.exceptions.base import ScFileException
from scfile.utils import convert
from scfile.utils.convert.auto import ModelFormats

from . import types
from .excepthook import excepthook


FilesType: TypeAlias = Sequence[types.PathType]
FilesMap: TypeAlias = dict[types.PathType, list[types.PathType]]

sys.excepthook = excepthook


@click.command(epilog=CLI.EPILOG)
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
    "--parse-skeleton",
    help="Parse armature in models (if presented)",
    is_flag=True,
)
@click.option(
    "--parse-animations",
    help="Parse animations in models (if presented)",
    is_flag=True,
)
@click.option(
    "--is-hdri",
    help="Parse textures as hdri (cubemaps)",
    is_flag=True,
)
@click.option(
    "--subdir",
    help="Recreate input subdirectories to output.",
    is_flag=True,
)
@click.option(
    "--no-overwrite",
    help="Do not overwrite file if already exists.",
    is_flag=True,
)
@click.version_option(package_name="sc-file")
@click.pass_context
def scfile(
    ctx: click.Context,
    paths: FilesType,
    output: Optional[types.PathType],
    model_formats: ModelFormats,
    parse_skeleton: bool,
    parse_animations: bool,
    is_hdri: bool,
    subdir: bool,
    no_overwrite: bool,
):
    if not paths:
        no_args(ctx)
        return

    if subdir and not output:
        print(Prefix.WARN, "[b]--subdir[/] flag cannot be used without specifying [b]--output[/] option.")

    files = paths_to_files_map(paths)

    if not files:
        print(Prefix.ERROR, "No supported files found in provided arguments.")
        print(CLI.FORMATS)
        return

    for root, sources in files.items():
        for source in sources:
            dest = output

            if output and subdir:
                dest = output / source.relative_to(root.parent).parent

            try:
                convert.auto(
                    source=source,
                    output=dest,
                    model_options=ModelOptions(
                        parse_skeleton=parse_skeleton,
                        parse_animations=parse_animations,
                    ),
                    texture_options=TextureOptions(is_hdri=is_hdri),
                    image_options=ImageOptions(),
                    model_formats=model_formats,
                    overwrite=not no_overwrite,
                )
                print(Prefix.INFO, f"File '{source.name}' converted to '{dest or source.parent}'")

            except ScFileException as err:
                print(Prefix.ERROR, str(err))

            except Exception as err:
                print(Prefix.EXCEPTION, str(err))


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
