"""
Shared options for handlers.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from scfile.consts import DefaultModelFormats, Formats


OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: list[OnConflict] = ["overwrite", "rename", "skip"]


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

    @property
    def default_model_formats(self) -> Formats:
        """Default output formats for models based on current options."""

        if self.skeleton:
            return DefaultModelFormats.ON_SKELETON

        return DefaultModelFormats.STANDARD
