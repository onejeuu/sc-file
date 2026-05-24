"""
HDRI Format.

:Name: **Object Layer**
:Type: **🧱 Texture Decoder (Cubemap)**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#ol-object-layer-ol-bt>`_
:Suffix: ``.ol``
:Support: ``✅ Full``
:Features: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_XY`` (``ATI2``), ``RGBA32F`` (``DX10``)

Example::

    from scfile import formats

    with formats.hdri.OlCubemapDecoder("cubemap.ol") as hdri:
        data = hdri.decode()
"""

from .decoder import OlCubemapDecoder


__all__ = ("OlCubemapDecoder",)
