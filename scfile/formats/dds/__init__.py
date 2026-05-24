"""
DDS Format.

:Name: **DirectDraw Surface**
:Type: **🧱 Texture Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/DirectDraw_Surface>`_
:Suffix: ``.dds``
:Support: ``✅ Full``
:Features: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_XY`` (``ATI2``), ``RGBA32F`` (``DX10``)

Example::

    from scfile import formats

    with formats.dds.DdsEncoder(data) as dds:
        dds.encode().save("output.dds")
"""

from .encoder import DdsEncoder


__all__ = ("DdsEncoder",)
