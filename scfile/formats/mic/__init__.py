"""
MIC Format.

:Name: **Media Image Container**
:Handler: :class:`~scfile.formats.mic.decoder.MicDecoder`
:Content: :class:`~scfile.content.base.ImageContent`
:Suffix: ``.mic``
:Support: ``✅ FULL``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mic

Usage Example::

    from scfile import formats

    with formats.MicDecoder("image.mic") as mic:
        data = mic.decode()
"""

from .decoder import MicDecoder


__all__ = ("MicDecoder",)
