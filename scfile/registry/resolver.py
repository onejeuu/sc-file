"""
Format resolution.
"""

from pathlib import Path
from typing import Optional

from scfile.consts import SUPPORTED_NBT
from scfile.options import Options
from scfile.core import ModelContent
from scfile.enums import FileFormat
from scfile.types import PathLike

from .registry import Encoder, FormatSpec, Registry


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
        name = path.name.lower()
        if name in SUPPORTED_NBT:
            return self.registry.get(FileFormat.NBT)

        entry = self.registry.get(path.suffix)
        if entry is None or entry.decoder is None:
            return None
        return entry

    def targets(
        self,
        source: FormatSpec,
        options: Optional[Options] = None,
    ) -> dict[FileFormat, Encoder]:
        """Select output handlers for direct conversion."""

        available = self.registry.targets(source.format)
        if not available:
            return {}

        options = options or Options()
        if issubclass(source.content, ModelContent):
            selected = options.model_formats or options.default_model_formats
            return {fmt: available[fmt] for fmt in selected if fmt in available}

        if len(available) == 1:
            return available

        return {}
