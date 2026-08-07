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

    paths = list(map(Path, sources))
    resolved = sorted({path.resolve() for path in paths if path.exists()})

    unique: types.FilesPaths = []
    for path in resolved:
        if not any(path.is_relative_to(parent) for parent in unique):
            unique.append(path)

    return unique


def walk(
    sources: types.FilesSources,
    whitelist: types.FilesWhitelist | None = None,
    parent: bool = False,
) -> types.FilesWalk:
    """Walk through files in given sources, optionally filtering by whitelist."""

    paths = resolve(sources)
    paths = list(map(str, paths))
    filters = whitelist or REGISTRY.supported_inputs
    allowed = tuple(value.lower() for value in filters)
    suffixes = tuple(value for value in allowed if value.startswith("."))
    names = {value for value in allowed if not value.startswith(".")}

    for root in paths:
        base = os.path.dirname(root) if parent else root

        if os.path.isfile(root):
            name = os.path.basename(root).lower()
            if name in names or name.endswith(suffixes):
                yield types.FileEntry(
                    root=root,
                    path=root,
                    relpath=os.path.relpath(root, base),
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
                                    relpath=os.path.relpath(entry.path, base),
                                )

            except PermissionError:
                continue


def destination(
    relpath: str,
    relative: bool,
    output: str | None,
) -> str | None:
    """Resolve destination path based on options."""

    if relative and output:
        return os.path.join(output, os.path.dirname(relpath))

    return output
