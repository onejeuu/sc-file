"""
Data types for core classes.
"""

import os
import pathlib
from typing import Any, TypeAlias, TypeVar

from .context import FileContent


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path
EncoderContext: TypeAlias = dict[str, Any]

Content = TypeVar("Content", bound=FileContent)
