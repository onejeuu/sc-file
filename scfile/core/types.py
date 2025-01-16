from typing import TypeVar

from .meta import FileContext, FileOptions


Context = TypeVar("Context", bound=FileContext)
Options = TypeVar("Options", bound=FileOptions)
