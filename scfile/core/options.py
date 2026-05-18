"""
Shared user options between decoder and encoder.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from scfile.consts import DefaultModelFormats, Formats


OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: list[OnConflict] = ["overwrite", "rename", "skip"]


@dataclass
class UserOptions:
    """Shared user options between decoder and encoder."""

    model_formats: Optional[Formats] = None
    parse_skeleton: bool = False
    parse_animation: bool = False
    parse_region_raw: bool = False
    on_conflict: OnConflict = "overwrite"

    @property
    def default_model_formats(self) -> Formats:
        if self.parse_skeleton:
            return DefaultModelFormats.ON_SKELETON
        return DefaultModelFormats.STANDARD
