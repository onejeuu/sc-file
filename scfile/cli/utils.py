"""
CLI wrapper small utils.
"""

from pathlib import Path

from rich import print

from scfile.consts import NBT_FILENAMES, SUPPORTED_SUFFIXES, Formats
from scfile.enums import L

from . import types


def check_feature_unsupported(user_formats: Formats, unsupported_formats: Formats, feature: str) -> None:
    """Checks that user formats contain unsupported feature."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: fmt.suffix, matching_formats))
        print(L.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature}.")


def is_supported(path: Path) -> bool:
    """Checks that file is supported (by suffix)."""
    return path.is_file() and (path.suffix in SUPPORTED_SUFFIXES or path.name in NBT_FILENAMES)


def paths_to_files_map(paths: types.FilesPaths) -> types.FilesIter:
    """Maps parent directories to their supported files."""
    for path in paths:
        if not path.exists():
            continue

        path = path.resolve()

        if path.is_file():
            if is_supported(path):
                yield path.parent, path

        elif path.is_dir():
            for file in path.rglob("*"):
                if is_supported(file):
                    yield path, file


def output_to_destination(
    root: Path, source: Path, output: types.OutputDir, relative: bool, parent: bool
) -> types.OutputDir:
    """Output path with source relative subdirectory appended if relative flag."""
    if relative and output:
        basedir = root.parent if parent else root
        return output / source.relative_to(basedir).parent
    return output
