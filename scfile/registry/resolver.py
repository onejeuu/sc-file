"""
Format resolution.
"""

from pathlib import Path
from typing import Any, Optional

from scfile.core import Encoder, ModelContent
from scfile.enums import FileFormat
from scfile.options import ConvertOptions
from scfile.types import PathLike

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
        source: PathLike,
    ) -> FormatSpec | None:
        """Resolve a registered source format from file path."""

        path = Path(source)
        entry = self.registry.get(path.name) or self.registry.get(path.suffix)
        if entry is None or entry.decoder is None:
            return None
        return entry

    def targets(
        self,
        source: FormatSpec,
        options: Optional[ConvertOptions] = None,
    ) -> dict[FileFormat, type[Encoder[Any, Any]]]:
        """Select output handlers for direct conversion."""

        available = self.registry.targets(source.format)
        if not available:
            return {}

        options = options or ConvertOptions()
        if issubclass(source.content, ModelContent):
            selected = options.formats or options.default_formats
            return {fmt: available[fmt] for fmt in selected if fmt in available}

        if len(available) == 1:
            return available

        return {}
