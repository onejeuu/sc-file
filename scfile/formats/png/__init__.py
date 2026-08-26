"""
PNG Format.

:Name: **Portable Network Graphics**
:Handler: :class:`~scfile.formats.png.encoder.PngEncoder`
:Content: :class:`~scfile.content.base.ImageContent`
:Suffix: ``.png``
:Support: ``✅ FULL``
:Wiki: https://en.wikipedia.org/wiki/Portable_Network_Graphics

Usage Example::

    from scfile import formats

    with formats.PngEncoder(data) as png:
        png.save("output.png")
"""

from .encoder import PngEncoder


__all__ = ("PngEncoder",)
