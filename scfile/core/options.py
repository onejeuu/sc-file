"""
Shared user options for decoders and encoders.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from scfile.consts import DefaultModelFormats, Formats


OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: list[OnConflict] = ["overwrite", "rename", "skip"]


@dataclass
class Options:
    """Shared settings for decoding and encoding."""

    model_formats: Optional[Formats] = None
    """Preferred output formats for models, :meth:`default_model_formats` used on unset."""

    skeleton: bool = False
    """Decode and Encode skeleton bones from models."""

    animation: bool = False
    """Decode and Encode built-in animation clips from models."""

    chunks_raw: bool = False
    """Keep raw block IDs in chunks data without lookup table replacement."""

    on_conflict: OnConflict = "overwrite"
    """
    Action when output file already exists.

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
