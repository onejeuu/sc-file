"""
NBT Format.

:Name: **Named Binary Tag**
:Type: **⚙️ NBT Decoder**
:Wiki: `<https://minecraft.wiki/w/NBT_format>`_
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.nbt.NbtDecoder("itemnames.dat") as nbt:
        data = nbt.decode()
"""

from .decoder import NbtDecoder
from .enums import Tag


__all__ = ("NbtDecoder", "Tag")
