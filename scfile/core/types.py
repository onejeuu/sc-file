"""
Data types for core classes.
"""

import os
import pathlib
from typing import Any, Optional, TypeAlias, TypeVar

from .context import FileContent


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path
OutputDir: TypeAlias = Optional[PathLike]
EncoderContext: TypeAlias = dict[str, Any]

Content = TypeVar("Content", bound=FileContent)
