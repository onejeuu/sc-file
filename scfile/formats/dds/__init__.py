"""
DDS Format.

:Name: **DirectDraw Surface**
:Handler: :class:`~scfile.formats.dds.encoder.DdsEncoder`
:Content: :class:`~scfile.content.base.TextureContent`
:Suffix: ``.dds``
:Support: ``✅ FULL``
:Formats: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_X`` (``ATI1``), ``DXN_XY`` (``ATI2``), ``RGBA32F`` (``DX10``)
:Wiki: https://en.wikipedia.org/wiki/DirectDraw_Surface

Usage Example::

    from scfile import formats

    with formats.DdsEncoder(data) as dds:
        dds.save("output.dds")
"""

from .encoder import DdsEncoder


__all__ = ("DdsEncoder",)
