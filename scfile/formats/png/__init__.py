"""
PNG Format.

:Name: **Portable Network Graphics**
:Type: **🖼️ Image Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/PNG>`_
:Suffix: ``.png``
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.png.PngEncoder(data) as png:
        png.encode().save("output.png")
"""

from .encoder import PngEncoder


__all__ = ("PngEncoder",)
