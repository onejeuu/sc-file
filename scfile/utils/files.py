import sys
from pathlib import Path

from rich import print

from scfile import types
from scfile.consts import NBT_FILENAMES, SUPPORTED_SUFFIXES, Formats
from scfile.enums import L


def check_feature_unsupported(
    user_formats: Formats,
    unsupported_formats: Formats,
    feature: str,
) -> None:
    """Checks that user formats contain unsupported feature."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: fmt.suffix, matching_formats))
        print(L.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature}.")


def is_supported(
    path: types.Path,
) -> bool:
    """Checks that file is supported (by suffix)."""
    return path.is_file() and (path.suffix in SUPPORTED_SUFFIXES or path.name in NBT_FILENAMES)


def clean_source_paths(
    sources: types.FilesSources,
) -> list[types.Path]:
    resolved = sorted({Path(src).resolve() for src in sources if Path(src).exists()})
    clean: list[types.Path] = []
    for path in resolved:
        if not any(path.is_relative_to(root) for root in clean):
            clean.append(path)
    return clean


def paths_to_files_map(
    paths: types.FilesPaths,
) -> types.FilesIter:
    """Maps parent directories to their supported files."""
    for path in clean_source_paths(paths):
        if path.is_file():
            if is_supported(path):
                yield path.parent, path
        elif path.is_dir():
            for file in path.rglob("*"):
                if is_supported(file):
                    yield path, file


def output_to_destination(
    root: types.Path,
    source: types.Path,
    output: types.Output,
    relative: bool,
    parent: bool,
) -> types.Output:
    """Output path with source relative subdirectory appended if relative flag."""
    if relative and output:
        basedir = root.parent if parent else root
        return output / source.relative_to(basedir).parent
    return output


def get_resource(
    path: types.PathLike,
) -> types.Path:
    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / path

    root = Path(__file__).parent.parent.absolute()
    gui = root / "gui"

    return gui / path
