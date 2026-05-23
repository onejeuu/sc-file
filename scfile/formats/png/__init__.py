"""
PNG Format.

:Type: Image Encoder
:Name: Portable Network Graphics
:Wiki: `<https://en.wikipedia.org/wiki/PNG>`_

Example::

    from scfile import formats

    with formats.png.PngEncoder(data) as png:
        png.encode().save("output.png")
"""

from .encoder import PngEncoder


__all__ = ("PngEncoder",)
