"""
OL CUBEMAP Format (Deprecated).

:Name: **Object Layer**
:Type: **🧱 Texture Decoder (Cubemap)**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#ol-object-layer-ol-bt>`_
:Suffix: ``.ol``
:Support: ``⚠️ Deprecated``
:Features: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_X`` (``ATI1``), ``DXN_XY`` (``ATI2``), ``RGBA32F`` (``DX10``)

Example::

    from scfile import formats

    with formats.ol.OlDecoder("cubemap.ol") as ol:
        data = ol.decode()
"""

from .decoder import OlCubemapDecoder


__all__ = ("OlCubemapDecoder",)
