"""
TEXARR Format.

:Name: **Texture Array**
:Handler: :class:`~scfile.formats.texarr.decoder.TexarrDecoder`
:Content: :class:`~scfile.content.base.ArchiveContent`
:Suffix: ``.texarr``
:Support: ``✅ FULL``
:Wiki: https://sc-file.rtfd.io/page/formats.html#texarr

Usage Example::

    from scfile import formats

    with formats.TexarrDecoder("blocks.texarr") as texarr:
        data = texarr.decode()
"""

from .decoder import TexarrDecoder


__all__ = ("TexarrDecoder",)
