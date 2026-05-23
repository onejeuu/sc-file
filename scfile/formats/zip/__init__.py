"""
ZIP Format.

:Type: Texture Array Encoder
:Name: ZIP
:Wiki: `<https://en.wikipedia.org/wiki/ZIP_(file_format)>`_

Example::

    from scfile import formats

    with formats.zip.TexarrEncoder(data) as zip:
        zip.encode().save("output.zip")
"""

from .encoder import TexarrEncoder


__all__ = ("TexarrEncoder",)
