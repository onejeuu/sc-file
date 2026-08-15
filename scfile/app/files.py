import os
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

from scfile import types
from scfile.app.events import TaskError
from scfile.formats import registry


class FileEntry(NamedTuple):
    root: str
    path: str


def resource(
    path: types.SourceLike,
) -> types.SourcePath:
    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / path

    app = Path(__file__).parent.absolute()
    gui = app / "gui"

    return gui / path


def resolve(
    sources: Iterable[types.SourceLike],
) -> list[Path]:
    paths = {Path(source).resolve(strict=False) for source in sources}
    return sorted(path for path in paths if not any(parent in paths for parent in path.parents))


# TODO: replace taskerror
def scan(
    sources: Iterable[types.SourceLike],
    filters: Iterable[str] | None = None,
) -> Iterator[FileEntry | TaskError]:
    selected = filters or registry.filters()
    allowed = tuple(value.lower() for value in selected)
    suffixes = tuple(value for value in allowed if value.startswith("."))
    names = {value for value in allowed if not value.startswith(".")}

    for path in resolve(sources):
        root = str(path)

        if os.path.isfile(root):
            name = os.path.basename(root).lower()
            if name in names or name.endswith(suffixes):
                yield FileEntry(root, root)
            continue

        stack = [root]
        while stack:
            current = stack.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        try:
                            if entry.is_symlink() or entry.is_junction():
                                continue
                            if entry.is_dir():
                                stack.append(entry.path)
                                continue
                            if not entry.is_file():
                                continue

                        except OSError as error:
                            yield TaskError(error, source=entry.path)
                            continue

                        name = entry.name.lower()
                        if name in names or name.endswith(suffixes):
                            yield FileEntry(root, entry.path)

            except OSError as error:
                yield TaskError(error, source=current)


def walk(
    sources: Iterable[types.SourceLike],
    filters: Iterable[str] | None = None,
) -> Iterator[FileEntry]:
    for item in scan(sources, filters):
        if isinstance(item, FileEntry):
            yield item


def count(
    sources: Iterable[types.SourceLike],
    filters: Iterable[str] | None = None,
) -> int:
    return sum(isinstance(item, FileEntry) for item in scan(sources, filters))


def destination(
    path: str,
    base: str | None,
    output: str | None,
) -> str | None:
    if base and output:
        relative = os.path.relpath(path, base)
        return os.path.join(output, os.path.dirname(relative))

    return output
