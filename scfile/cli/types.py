"""
Data types for CLI wrapper.
"""

import pathlib
from typing import Iterator, Optional, Sequence, Tuple, TypeAlias

import click

from scfile.consts import OutputFormats


PathType = pathlib.Path

FilesPaths: TypeAlias = Sequence[PathType]
FilesIter: TypeAlias = Iterator[Tuple[PathType, PathType]]
OutputDir: TypeAlias = Optional[PathType]

Files = click.Path(path_type=PathType, dir_okay=True, file_okay=True, exists=True, resolve_path=True)
Output = click.Path(path_type=PathType, dir_okay=True, file_okay=False)
Formats = click.Choice(list(OutputFormats.MODELS), case_sensitive=False)
