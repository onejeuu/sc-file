import os
from collections.abc import Sequence
from pathlib import Path

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

type Formats = Sequence[FileFormat]
"""Sequence of file formats."""

type FormatLike = str | FileFormat
"""File format represented by its enum, value, or suffix."""
