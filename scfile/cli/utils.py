"""
CLI wrapper small utils.
"""

from collections import defaultdict
from pathlib import Path

import click
from rich import print

from scfile.cli.enums import Prefix
from scfile.consts import CLI, SUPPORTED_SUFFIXES, ModelFormats

from . import types


def no_args(ctx: click.Context) -> None:
    """Prints help message when no arguments are provided."""
    print("[b yellow]No arguments provided. Showing help:[/]")
    print()
    click.echo(f"{ctx.get_help()}")
    click.pause(CLI.PAUSE_TEXT)


def check_feature_unsupported(user_formats: ModelFormats, unsupported_formats: ModelFormats, feature_name: str):
    """Check if user formats contain unsupported features and return matching formats."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: f".{fmt.value}", matching_formats))
        print(Prefix.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature_name}.")


def is_supported(path: Path) -> bool:
    """Checks that file is supported (by suffix)."""
    return path.is_file() and path.suffix in SUPPORTED_SUFFIXES


def filter_files(files: types.FilesPaths):
    """Filters paths to keep only supported files."""
    return list(filter(is_supported, files))


def paths_to_files_map(paths: types.FilesPaths) -> types.FilesMap:
    """Maps parent directories to their contained supported files."""
    files_map: types.FilesMap = defaultdict(list)
    resolved_symlinks: set[types.PathType] = set()

    for path in paths:
        if path.is_file():
            files_map[path.parent].extend(filter_files([path]))

        elif path.is_dir():
            if path.is_symlink():
                resolved = path.resolve()
                if resolved in resolved_symlinks:
                    continue
                resolved_symlinks.add(resolved)

            files_map[path].extend(filter_files(list(path.rglob("**/*"))))

    valid_files: types.FilesMap = {key: value for key, value in files_map.items() if value}
    return valid_files
