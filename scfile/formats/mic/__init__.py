"""
MIC Format.

:Name: **Media Image Container**
:Type: **🖼️ Image Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mic-media-image-container>`_
:Suffix: ``.mic``
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.mic.MicDecoder("image.mic") as mic:
        data = mic.decode()
"""

from .decoder import MicDecoder


__all__ = ("MicDecoder",)
