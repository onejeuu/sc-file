import warnings
from typing import Optional

from scfile.core import IOStream, Options
from scfile.formats.ol import OlDecoder


class OlCubemapDecoder(OlDecoder):
    """Deprecated compatibility name for :class:`OlDecoder`."""

    def __init__(self, stream: IOStream, options: Optional[Options] = None):
        warnings.warn(
            "OlCubemapDecoder is deprecated and will be removed in a future release; use OlDecoder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(stream, options)
