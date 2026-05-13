import os
import sys
from pathlib import Path

from scfile import types
from scfile.consts import ALLOWED_SUFFIXES


def resource(
    path: types.PathLike,
) -> types.Path:
    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / path

    root = Path(__file__).parent.parent.absolute()
    gui = root / "gui"

    return gui / path


def resolve(
    sources: types.FilesSources,
) -> types.FilesPaths:
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
    paths = resolve(sources)
    paths = list(map(str, paths))
    whitelist = tuple(whitelist or ALLOWED_SUFFIXES)

    for root in paths:
        if not os.path.exists(root):
            continue

        base = os.path.dirname(root) if parent else root

        if os.path.isfile(root):
            if root.lower().endswith(whitelist):
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
                        if entry.is_dir():
                            stack.append(entry.path)
                        elif entry.is_file():
                            if entry.name.lower().endswith(whitelist):
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
    if relative and output:
        return os.path.join(output, os.path.dirname(relpath))
    return output
