"""
Base class for format handlers that own a binary resource.
"""

from abc import ABC
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Self

from scfile import exceptions
from scfile.enums import ByteOrder, FileFormat, HandlerState
from scfile.io.base import FileMode, IOStream, StructIO
from scfile.options import HandlerOptions


type HandlerContext = dict[str, Any]


class Handler[IOType: StructIO](ABC):
    """Base class for handlers that own an open binary resource."""

    format: FileFormat = FileFormat.NONE
    """Associated file format."""

    signature: bytes | None = None
    """Expected file signature."""

    io_factory: type[IOType]
    """Binary I/O used by the handler."""

    io: IOType
    """Owned binary I/O instance."""

    order: ByteOrder = ByteOrder.LITTLE
    """Default byte order."""

    options: HandlerOptions
    """Shared handlers options."""

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
        )
        self._ctx: HandlerContext = {}
        self._state = HandlerState.INITIAL

    @property
    def suffix(self) -> str:
        return self.format.suffix

    @property
    def location(self) -> str:
        return self.io.location

    @property
    def closed(self) -> bool:
        return self.io.closed

    @property
    def state(self) -> HandlerState:
        """Current operation lifecycle state."""

        return self._state

    @property
    def context(self) -> Mapping[str, Any]:
        """Format-specific processing context for diagnostics."""

        return MappingProxyType(self._ctx)

    def close(self) -> None:
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
