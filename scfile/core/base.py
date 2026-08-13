"""
Base class for format handlers that own a binary resource.
"""

from abc import ABC
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, ClassVar, Self

from scfile import exceptions
from scfile.enums import ByteOrder, FileFormat, HandlerState
from scfile.io.base import StructIO


from scfile.options import Options


type HandlerContext = dict[str, Any]


class Handler[IOType: StructIO[Any]](ABC):
    """Base class for handlers that own an open binary resource."""

    format: ClassVar[FileFormat] = FileFormat.NONE
    """Associated file format."""

    signature: ClassVar[bytes | None] = None
    """Expected file signature."""

    order: ClassVar[ByteOrder] = ByteOrder.LITTLE
    """Default byte order."""

    io: IOType
    """Owned binary I/O instance."""

    options: Options
    """Processing and conversion options shared by the handler."""

    def __init__(
        self,
        io: IOType,
        options: Options,
    ):
        """
        Args:
            io: Structured binary IO owned by the handler.
        """

        self.io = io
        self.options = options
        self._ctx: HandlerContext = {}
        self._state = HandlerState.INITIAL

    @classmethod
    def suffix(cls) -> str:
        """Return the suffix associated with this handler format."""

        return cls.format.suffix

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
