"""
LANG Format.

:Name: **Language Properties**
:Handler: :class:`~scfile.formats.lang.decoder.LangDecoder`
:Content: :class:`~scfile.content.base.DocumentContent`
:Suffix: ``.lang``
:Support: ``✅ FULL``

Usage Example::

    from scfile import formats

    with formats.LangDecoder("en.lang") as lang:
        data = lang.decode()
"""

from .decoder import LangDecoder


__all__ = ("LangDecoder",)
