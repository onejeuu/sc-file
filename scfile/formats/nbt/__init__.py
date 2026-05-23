"""
NBT Format.

:Type: NBT Decoder
:Name: Named Binary Tag
:Wiki: `<https://minecraft.wiki/w/NBT_format>`_

Example::

    from scfile import formats

    with formats.nbt.NbtDecoder("itemnames.dat") as nbt:
        data = nbt.decode()
"""

from .decoder import NbtDecoder
from .enums import Tag


__all__ = ("NbtDecoder", "Tag")
