"""
Shared user options between decoder and encoder.
"""

from dataclasses import dataclass
from typing import Optional

from scfile.consts import DefaultModelFormats, Formats


@dataclass
class UserOptions:
    """Shared user options between decoder and encoder."""

    model_formats: Optional[Formats] = None
    parse_skeleton: bool = False
    parse_animation: bool = False
    overwrite: bool = True

    @property
    def default_model_formats(self):
        if self.parse_skeleton:
            return DefaultModelFormats.SKELETON
        return DefaultModelFormats.STANDARD
