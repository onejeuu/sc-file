"""
HDRI Format.

:Type: Texture (Cubemap) Decoder
:Name: Object Layer
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#ol-object-layer-ol-bt>`_

Example::

    from scfile import formats

    with formats.hdri.OlCubemapDecoder("cubemap.ol") as hdri:
        data = hdri.decode()
"""

from .decoder import OlCubemapDecoder


__all__ = ("OlCubemapDecoder",)
