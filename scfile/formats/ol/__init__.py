"""
OL Format.

:Name: **Object Layer**
:Handler: :class:`~scfile.formats.ol.decoder.OlDecoder`
:Content: :class:`~scfile.content.base.TextureContent`
:Suffix: ``.ol``
:Support: ``✅ FULL``
:Formats: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_X`` (``ATI1``), ``DXN_XY`` (``ATI2``), ``RGBA32F`` (``DX10``)
:Wiki: https://sc-file.rtfd.io/page/formats.html#ol

Usage Example::

    from scfile import formats

    with formats.OlDecoder("texture.ol") as ol:
        data = ol.decode()
"""

from . import enums, formats
from .decoder import OlDecoder
from .enums import TextureKind


__all__ = (
    "OlDecoder",
    "TextureKind",
    "enums",
    "formats",
)
