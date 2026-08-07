"""
Format resolution.
"""

from pathlib import Path
from typing import Any, Optional

from scfile.core import Encoder, ModelContent
from scfile.options import Options
from scfile.types import SourceLike

from .registry import FormatSpec, Registry


class Resolver:
    """Select supported formats and output handlers."""

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

    def target(
        self,
        source: FormatSpec,
        options: Optional[Options] = None,
    ) -> type[Encoder[Any, Any]] | None:
        """Select one output handler for direct conversion."""

        available = self.registry.targets(source.format)
        if not available:
            return None

        options = options or Options()
        if issubclass(source.content, ModelContent):
            selected = options.model_format or options.default_format
            return available.get(selected)

        if len(available) == 1:
            return next(iter(available.values()))

        return None
