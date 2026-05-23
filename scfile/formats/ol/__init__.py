"""
OL Format.

:Type: Texture Decoder
:Name: Object Layer
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#ol-object-layer-ol-bt>`_

Example::

    from scfile import formats

    with formats.ol.OlDecoder("texture.ol") as ol:
        data = ol.decode()
"""

from . import exceptions, formats
from .decoder import OlDecoder


__all__ = (
    "OlDecoder",
    "exceptions",
    "formats",
)
