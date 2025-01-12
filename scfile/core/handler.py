from abc import ABC
from types import TracebackType
from typing import Generic, Optional, TypeVar

from scfile.enums import ByteOrder, FileMode
from scfile.io.base import StructIOBase

from .context import FileContext


Context = TypeVar("Context", bound=FileContext)
Opener = TypeVar("Opener", bound=StructIOBase)


class FileHandler(Generic[Context, Opener], ABC):
    # TODO: check context memory release
    def __init__(self, ctx: Context, buffer: Opener):
        self.buffer = buffer
        self.ctx = ctx

    mode: FileMode
    order: ByteOrder = StructIOBase.order
    signature: Optional[bytes] = None

    def close(self):
        self.buffer.close()

    def __enter__(self):
        return self

    # TODO: check validation needed before closing or not
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()
