import os
import pathlib
from collections.abc import Iterable, Iterator, Sequence
from typing import NamedTuple, Optional

from .enums import FileFormat


Path = pathlib.Path
type PathLike = str | Path | os.PathLike[str]
"""Path represented as string, pathlib.Path, or OS path-like object."""


type Output = Path | None
"""Optional output path."""
type OutputLike = Optional[PathLike]
"""Optional path-like output."""

type FilesWhitelist = Iterable[str]
"""Iterable of file suffixes for filtering."""
type FilesPaths = Iterable[Path]
"""Iterable of file paths."""
type FilesSources = Iterable[PathLike]
"""Iterable of path-like sources."""

type Formats = Sequence[FileFormat]
"""Sequence of file formats."""

type FormatLike = str | FileFormat
"""File format represented by its enum, value, or suffix."""


class FileEntry(NamedTuple):
    """File entry from directory walk."""

    root: str
    path: str
    relpath: str


type FilesWalk = Iterator[FileEntry]
"""Iterator over file entries."""
