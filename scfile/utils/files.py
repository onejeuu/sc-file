"""Basic file and path operations."""

import os
import sys
from pathlib import Path

from scfile import types
from scfile.registry import REGISTRY


def resource(
    path: types.SourceLike,
) -> types.SourcePath:
    """Resolve resource path, accounting for MEIPASS environment variable."""

    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / path

    root = Path(__file__).parent.parent.absolute()
    gui = root / "app/gui"

    return gui / path


def resolve(
    sources: types.FilesSources,
) -> types.FilesPaths:
    """Normalize paths into a clean minimal set."""

    paths = {path.resolve() for source in sources if (path := Path(source)).exists()}
    return sorted(path for path in paths if not any(parent in paths for parent in path.parents))


def walk(
    sources: types.FilesSources,
    filters: types.FilesFilters | None = None,
) -> types.FilesWalk:
    """Walk through files in given sources, optionally filtering by name."""

    paths = resolve(sources)
    paths = list(map(str, paths))
    selected = filters or REGISTRY.supported_inputs
    allowed = tuple(value.lower() for value in selected)
    suffixes = tuple(value for value in allowed if value.startswith("."))
    names = {value for value in allowed if not value.startswith(".")}

    for root in paths:
        if os.path.isfile(root):
            name = os.path.basename(root).lower()
            if name in names or name.endswith(suffixes):
                yield types.FileEntry(
                    root=root,
                    path=root,
                )
            continue

        stack = [root]
        while stack:
            current = stack.pop()
            try:
                with os.scandir(current) as it:
                    for entry in it:
                        if entry.is_symlink() or entry.is_junction():
                            continue

                        if entry.is_dir():
                            stack.append(entry.path)

                        elif entry.is_file():
                            name = entry.name.lower()
                            if name in names or name.endswith(suffixes):
                                yield types.FileEntry(
                                    root=root,
                                    path=entry.path,
                                )

            except PermissionError:
                continue


def count(
    sources: types.FilesSources,
    filters: types.FilesFilters | None = None,
) -> int:
    """Count matching files without retaining them."""

    return sum(1 for _ in walk(sources, filters))


def destination(
    path: str,
    base: str | None,
    output: str | None,
) -> str | None:
    """Resolve destination path based on options."""

    if base and output:
        relative = os.path.relpath(path, base)
        return os.path.join(output, os.path.dirname(relative))

    return output
