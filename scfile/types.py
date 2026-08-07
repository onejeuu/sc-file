import os
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import NamedTuple, Optional

from .enums import FileFormat


type SourcePath = Path
"""Source path."""
type SourceLike = str | Path | os.PathLike[str]
"""Source path-like."""
type OutputPath = Optional[Path]
"""Optional output path."""
type OutputLike = Optional[str | Path | os.PathLike[str]]
"""Optional path-like output."""

type FilesWhitelist = Iterable[str]
"""Iterable of file suffixes for filtering."""
type FilesPaths = Iterable[SourcePath]
"""Iterable of file paths."""
type FilesSources = Iterable[SourceLike]
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
