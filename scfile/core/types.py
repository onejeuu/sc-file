from typing import TypeVar

from .context import FileContext
from .options import FileOptions


Context = TypeVar("Context", bound=FileContext)
Options = TypeVar("Options", bound=FileOptions)
