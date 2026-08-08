"""
Format resolution.
"""

from pathlib import Path
from scfile.types import SourceLike

from .registry import FormatSpec, Registry


class Resolver:
    """Resolve supported source formats."""

    def __init__(
        self,
        registry: Registry,
    ):
        self.registry = registry

    def resolve(
        self,
        source: SourceLike,
    ) -> FormatSpec | None:
        """Resolve a registered source format from file path."""

        path = Path(source)
        entry = self.registry.get(path.name) or self.registry.get(path.suffix)
        if entry is None or entry.decoder is None:
            return None
        return entry
