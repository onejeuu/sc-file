"""
Shared options for handlers.
"""

from dataclasses import dataclass
from typing import Literal

from scfile.enums import FileFormat
from scfile.types import Formats


type OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: list[OnConflict] = ["overwrite", "rename", "skip"]

DEFAULT_MODEL_FORMATS: Formats = (FileFormat.OBJ,)
"""Default output formats when skeleton processing is disabled."""

DEFAULT_SKELETON_FORMATS: Formats = (FileFormat.GLB,)
"""Default output formats when skeleton processing is enabled."""


@dataclass
class Options:
    """Shared handlers options."""

    model_formats: Formats | None = None
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

    @property
    def skeleton_enabled(self) -> bool:
        """Whether skeleton processing is enabled directly or by animation processing."""

        return self.skeleton or self.animation

    @property
    def default_model_formats(self) -> Formats:
        """Default output formats for models based on current options."""

        if self.skeleton_enabled:
            return DEFAULT_SKELETON_FORMATS

        return DEFAULT_MODEL_FORMATS
