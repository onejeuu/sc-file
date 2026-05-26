import os
import pathlib
from typing import Iterable, Iterator, NamedTuple, Optional, Sequence, TypeAlias

from .enums import FileFormat


Formats: TypeAlias = Sequence[FileFormat]
"""Sequence of file formats."""

Path = pathlib.Path
PathLike: TypeAlias = str | Path | os.PathLike[str]
"""Path represented as string, pathlib.Path, or OS path-like object."""

Output: TypeAlias = Optional[Path]
"""Optional output path."""
OutputLike: TypeAlias = Optional[PathLike]
"""Optional path-like output."""

FilesWhitelist: TypeAlias = Iterable[str]
"""Iterable of file suffixes for filtering."""
FilesPaths: TypeAlias = Iterable[Path]
"""Iterable of file paths."""
FilesSources: TypeAlias = Iterable[PathLike]
"""Iterable of path-like sources."""


class FileEntry(NamedTuple):
    """File entry from directory walk."""

    root: str
    path: str
    relpath: str


FilesWalk: TypeAlias = Iterator[FileEntry]
"""Iterator over file entries."""
