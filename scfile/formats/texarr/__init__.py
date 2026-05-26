"""
TEXARR Format.

:Name: **Texture Array**
:Type: **🗃️ TextureArray Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#texarr-texture-array-texarr-bt>`_
:Suffix: ``.texarr``
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.texarr.TexarrDecoder("blocks.texarr") as texarr:
        data = texarr.decode()
"""

from .decoder import TexarrDecoder


__all__ = ("TexarrDecoder",)
