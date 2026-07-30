"""
Shared options for handlers.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from scfile.enums import FileFormat
from scfile.structures.models import Feature
from scfile.types import Formats


OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: list[OnConflict] = ["overwrite", "rename", "skip"]

DEFAULT_MODEL_FORMATS: Formats = (FileFormat.OBJ,)
"""Default output formats when skeleton parsing is disabled."""

DEFAULT_SKELETON_FORMATS: Formats = (FileFormat.GLB,)
"""Default output formats when skeleton parsing is enabled."""


@dataclass
class Options:
    """Shared handlers options."""

    model_formats: Optional[Formats] = None
    """Preferred output formats for models, :meth:`default_model_formats` used on unset."""

    skeleton: bool = False
    """Handle skeleton bones from models."""

    animation: bool = False
    """Handle built-in animation clips from models."""

    raw_blocks: bool = False
    """Keep raw block IDs in chunks without lookup table replacement."""

    full_chunk: bool = False
    """Handle full chunk data including metadata (no export)."""

    on_conflict: OnConflict = "overwrite"
    """
    Action on output file name conflict (if already exists).

    - `"overwrite"` Replace the existing file.
    - `"skip"` Keep the existing file.
    - `"rename"` Add a numeric suffix (e.g. `model (1).obj`).
    """

    def includes(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether processing a feature is enabled."""

        if feature is Feature.ANIMATION or feature.parent is Feature.ANIMATION:
            return self.animation

        if feature is Feature.SKELETON:
            return self.skeleton or self.animation

        return True

    @property
    def default_model_formats(self) -> Formats:
        """Default output formats for models based on current options."""

        if self.includes(Feature.SKELETON):
            return DEFAULT_SKELETON_FORMATS

        return DEFAULT_MODEL_FORMATS
