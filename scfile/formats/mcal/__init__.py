"""
MCAL Format.

:Type: Model Decoder
:Name: Animation Library
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#mcal-animation-library-mcal-bt>`_

Example::

    from scfile import formats

    with formats.mca.McalDecoder("anims.mcal") as mcal:
        data = mcal.decode()
"""

from .decoder import McalDecoder


__all__ = ("McalDecoder",)
