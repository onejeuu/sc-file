"""
SIGN Format.

:Name: **Texture Signatures**
:Handler: :class:`~scfile.formats.sign.decoder.SignDecoder`
:Content: :class:`~scfile.content.base.DocumentContent`
:Suffix: ``.sign``
:Support: ``✅ FULL``

Usage Example::

    from scfile import formats

    with formats.SignDecoder("textures.sign") as sign:
        data = sign.decode()
"""

from .decoder import SignDecoder


__all__ = ("SignDecoder",)
