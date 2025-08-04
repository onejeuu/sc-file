from typing import TypeVar

from scfile.core.context import FileContent
from scfile.types import OutputDir, PathLike


Content = TypeVar("Content", bound=FileContent)


__all__ = (
    "Content",
    "OutputDir",
    "PathLike",
)
