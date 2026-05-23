"""
MIC Format.

:Type: Image Decoder
:Name: Media Image Container
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#mic-media-image-container>`_

Example::

    from scfile import formats

    with formats.mic.MicDecoder("image.mic") as mic:
        data = mic.decode()
"""

from .decoder import MicDecoder


__all__ = ("MicDecoder",)
