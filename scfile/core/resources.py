"""Read-only resources shared by handlers within one operation."""

from collections.abc import Iterator, Mapping
from types import MappingProxyType
from typing import Any


class Resources(Mapping[str, Any]):
    """Container of resources shared by handlers in one operation."""

    __slots__ = ("_values",)

    def __init__(
        self,
        values: Mapping[str, Any] | None = None,
    ) -> None:
        """Create a resource container from a mapping of named objects."""

        self._values = MappingProxyType(dict(values) if values is not None else {})

    def __getitem__(self, key: str) -> Any:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)
