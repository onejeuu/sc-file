"""
NBT Format.

:Name: **Named Binary Tag**
:Handler: :class:`~scfile.formats.nbt.decoder.NbtDecoder`
:Content: :class:`~scfile.content.base.DocumentContent`
:Support: ``✅ FULL``
:Compression: None, ``gzip``, ``zstd``
:Wiki: https://minecraft.wiki/w/NBT_format

Usage Example::

    from scfile import formats

    with formats.NbtDecoder("itemnames.dat") as nbt:
        data = nbt.decode()
"""

from .decoder import NbtDecoder
from .filenames import SUPPORTED_FILENAMES


__all__ = ("SUPPORTED_FILENAMES", "NbtDecoder")
