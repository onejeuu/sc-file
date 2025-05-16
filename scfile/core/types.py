"""
Data types for core classes.
"""

import os
import pathlib
from typing import TypeAlias, TypeVar

from .context import FileContent


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path

Content = TypeVar("Content", bound=FileContent)
