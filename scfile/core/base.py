"""
Base class for resource-owning format handlers.
"""

from abc import ABC
from typing import Any, Generic, Optional, Self, TypeAlias, TypeVar

from scfile import exceptions
from scfile.enums import ByteOrder, FileFormat, HandlerState, UnicodeErrors
from scfile.io.base import FileMode, IOStream, StructIO

from .options import Options


TempContext: TypeAlias = dict[str, Any]
IOType = TypeVar("IOType", bound=StructIO)


class BaseFile(Generic[IOType], ABC):
    """Base class for handlers that own an open binary resource."""

    format: FileFormat = FileFormat.NONE
    """Associated file format."""

    signature: Optional[bytes] = None
    """Expected file signature."""

    io_factory: type[IOType]
    """Binary I/O used by the handler."""

    io: IOType
    """Owned binary I/O instance."""

    order: ByteOrder = ByteOrder.LITTLE
    """Default byte order."""

    unicode_errors: str = UnicodeErrors.REPLACE
    """UTF-8 error handling mode."""

    options: Options
    """Shared handlers options."""

    state: HandlerState
    """Current operation lifecycle state."""

    def __init__(
        self,
        stream: IOStream,
        mode: FileMode = "rb",
    ):
        """
        Args:
            stream: Source input. File path, bytes, or binary IO stream.
            mode: File mode (binary) for opening when ``stream`` is path.
        """

        self.io = self.io_factory(
            stream,
            mode,
            order=self.order,
            unicode_errors=self.unicode_errors,
        )
        self.ctx: TempContext = {}
        self.state = HandlerState.INITIAL

    @property
    def suffix(self) -> str:
        return self.format.suffix

    @property
    def location(self) -> str:
        return self.io.location

    @property
    def closed(self) -> bool:
        return self.io.closed

    def close(self) -> None:
        self.ctx = {}
        self.io.close()

    def _validate_state(
        self,
        operation: str,
        expected: HandlerState,
    ) -> None:
        if self.state is expected and not self.closed:
            return

        raise exceptions.HandlerStateError(
            operation,
            self.state,
            closed=self.closed,
            location=self.location,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        *_,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        closed = "closed" if self.closed else "open"
        return f"<{type(self).__name__} {self.location} [{closed}]>"
