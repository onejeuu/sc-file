import os
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import NamedTuple

from .enums import FileFormat


type PathLike = str | Path | os.PathLike[str]
"""Path represented as a string, pathlib path, or OS path-like object."""

type SourcePath = Path
"""Source path."""
type SourceLike = PathLike
"""Source path-like."""
type OutputPath = Path | None
"""Optional output path."""
type OutputLike = PathLike | None
"""Optional path-like output."""

type ResultPath = Path | None
"""Written result path, or ``None`` when output is skipped."""

type FilesFilters = Iterable[str]
"""Iterable of filename filters."""
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


type FilesWalk = Iterator[FileEntry]
"""Iterator over file entries."""
