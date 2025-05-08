"""
Data types for core classes.
"""

import os
import pathlib
from typing import TypeAlias, TypeVar

from .context import FileContent, FileOptions


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path

Content = TypeVar("Content", bound=FileContent)
Options = TypeVar("Options", bound=FileOptions)
