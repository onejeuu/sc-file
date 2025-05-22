"""
CLI wrapper small utils.
"""

from pathlib import Path

import click
from rich import print

from scfile.cli.enums import Prefix
from scfile.consts import CLI, SUPPORTED_SUFFIXES, ModelFormats

from . import types


def no_args(ctx: click.Context) -> None:
    """Prints help message when no arguments provided."""
    print(f"{ctx.get_help()}\n\n{Prefix.INVALID} No arguments provided. Showing help.")
    click.pause(CLI.PAUSE)


def check_feature_unsupported(user_formats: ModelFormats, unsupported_formats: ModelFormats, feature: str) -> None:
    """Checks that user formats contain unsupported feature."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: fmt.suffix, matching_formats))
        print(Prefix.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature}.")


def is_supported(path: Path) -> bool:
    """Checks that file is supported (by suffix)."""
    return path.is_file() and path.suffix in SUPPORTED_SUFFIXES


def paths_to_files_map(paths: types.FilesPaths) -> types.FilesIter:
    """Maps parent directories to their supported files."""

    for path in paths:
        path = path.resolve()

        if path.is_file():
            if is_supported(path):
                yield path.parent, path

        elif path.is_dir():
            for file in path.rglob("*"):
                if is_supported(file):
                    yield path, file
