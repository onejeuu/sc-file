"""Binary format handler base class."""

from abc import ABC
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, ClassVar, Self

from scfile import exceptions
from scfile.enums import ByteOrder, FileFormat, HandlerState
from scfile.io.base import StructIO
from scfile.options import Options


type HandlerContext = dict[str, Any]
"""Format-specific values retained for diagnostics."""


class Handler[IOType: StructIO[Any]](ABC):
    """
    Base class for binary format handlers.

    A handler owns structured I/O, options, and lifecycle state.
    """

    format: ClassVar[FileFormat] = FileFormat.NONE
    """File format handled by this class."""

    signature: ClassVar[bytes | None] = None
    """Expected binary signature, if defined."""

    order: ClassVar[ByteOrder] = ByteOrder.LITTLE
    """Default byte order for structured I/O."""

    io: IOType
    """Structured I/O owned by this handler."""

    options: Options
    """Options used by this handler."""

    def __init__(
        self,
        io: IOType,
        options: Options,
    ):
        """
        Initialize handler.

        Args:
            io: Structured binary I/O owned by the handler.
            options: Options shared by the handler.
        """

        self.io = io
        self.options = options
        self._ctx: HandlerContext = {}
        self._state = HandlerState.INITIAL

    @classmethod
    def suffix(cls) -> str:
        """Return the format suffix."""

        return cls.format.suffix

    @property
    def location(self) -> str:
        """Location of the owned binary resource."""

        return self.io.location

    @property
    def closed(self) -> bool:
        """Whether the owned binary resource is closed."""

        return self.io.closed

    @property
    def state(self) -> HandlerState:
        """Current operation lifecycle state."""

        return self._state

    @property
    def context(self) -> Mapping[str, Any]:
        """Read-only format-specific values retained for diagnostics."""

        return MappingProxyType(self._ctx)

    def close(self) -> None:
        """Close the owned binary resource."""

        self.io.close()

    def _validate_state(
        self,
        operation: str,
        expected: HandlerState,
    ) -> None:
        """Require an open handler in the expected lifecycle state."""

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
