"""
MCAL Format.

:Name: **Animation Library**
:Type: **🧊 Model Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mcal-animation-library-mcal-bt>`_
:Suffix: ``.mcal``
:Support: ``🚧 WIP``

Example::

    from scfile import formats

    with formats.mca.McalDecoder("anims.mcal") as mcal:
        data = mcal.decode()
"""

from .decoder import McalDecoder


__all__ = ("McalDecoder",)
