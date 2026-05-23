"""
DDS Format.

:Type: Texture Encoder
:Name: DirectDraw Surface
:Wiki: `<https://en.wikipedia.org/wiki/DirectDraw_Surface>`_

Example::

    from scfile import formats

    with formats.dds.DdsEncoder(data) as dds:
        dds.encode().save("output.dds")
"""

from .encoder import DdsEncoder


__all__ = ("DdsEncoder",)
