from typing import TypeVar

from .context import FileContent, FileOptions


Content = TypeVar("Content", bound=FileContent)
Options = TypeVar("Options", bound=FileOptions)
