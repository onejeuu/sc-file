"""
TEXARR Format.

:Type: Texture Array Decoder
:Name: Texture Array
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#texarr-texture-array-texarr-bt>`_

Example::

    from scfile import formats

    with formats.texarr.TexarrDecoder("blocks.texarr") as texarr:
        data = texarr.decode()
"""

from .decoder import TexarrDecoder


__all__ = ("TexarrDecoder",)
