import warnings
from typing import Optional

from scfile.core import Options
from scfile.io import IOStream
from scfile.formats.ol import OlDecoder


class OlCubemapDecoder(OlDecoder):
    """
    Compatibility name for :class:`~scfile.formats.ol.OlDecoder`.

    .. deprecated:: 5.2.0
        Use :class:`~scfile.formats.ol.OlDecoder` instead.
    """

    def __init__(self, stream: IOStream, options: Optional[Options] = None):
        warnings.warn(
            "OlCubemapDecoder is deprecated and will be removed in a future release; use OlDecoder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(stream, options)
