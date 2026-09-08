"""
MAP Format.

:Name: **Launcher Hash Mappings**
:Handler: :class:`~scfile.formats.hashmap.decoder.HashmapDecoder`
:Content: :class:`~scfile.content.base.DocumentContent`
:Suffix: ``.map``
:Support: ``✅ FULL``

Usage Example::

    from scfile import formats

    with formats.HashmapDecoder("runtime.map") as hashmap:
        data = hashmap.decode()
"""

from .decoder import HashmapDecoder


__all__ = ("HashmapDecoder",)
