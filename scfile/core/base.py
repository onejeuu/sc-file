"""Handler lifecycle abstraction."""

from abc import ABC
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any, ClassVar, Self

from scfile import exceptions
from scfile.enums import ByteOrder, FileFormat, HandlerState
from scfile.io.base import StructIO
from scfile.options import Options

from .resources import Resources


type HandlerContext = dict[str, Any]
"""Format specific working context shared across handler methods."""


class Handler[IOType: StructIO[Any]](ABC):
    """Binary resource handler base class."""

    format: ClassVar[FileFormat] = FileFormat.NONE
    """Format handled by this handler."""

    signature: ClassVar[bytes | None] = None
    """Expected binary signature."""

    order: ClassVar[ByteOrder] = ByteOrder.LITTLE
    """Default byte order for structured I/O."""

    io: IOType
    """Structured I/O owned by this handler."""

    options: Options
    """Options applied by this handler."""

    _resources: Resources
    """Resources shared by handlers in the same operation."""

    def __init__(
        self,
        io: IOType,
        options: Options,
        resources: Resources | None = None,
    ):
        """
        Initialize handler.

        Args:
            io: Structured binary I/O owned by the handler.
            options: Options shared by the handler.
            resources: Resources shared by handlers in the same operation.
        """

        self.io = io
        self.options = options
        self._resources = resources or Resources()
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
    def resources(self) -> Resources:
        """Resources shared by handlers in the same operation."""

        return self._resources

    def _requirements(self) -> Mapping[str, Callable[[], Any]]:
        """Describe resources required for processing and how to create them."""

        return {}

    def _resolve_resources(self) -> None:
        """Reuse supplied resources and prepare only missing requirements."""

        missing = {key: factory() for key, factory in self._requirements().items() if key not in self._resources}

        if missing:
            self._resources = Resources({**self._resources, **missing})

    @property
    def context(self) -> Mapping[str, Any]:
        """Read-only view of the format specific working context."""

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
