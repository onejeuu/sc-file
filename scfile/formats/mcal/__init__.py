"""
MCAL Format.

:Name: **Animation Library**
:Handler: :class:`~scfile.formats.mcal.decoder.McalDecoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.mcal``
:Support: ``🧪 EXPERIMENTAL``
:Features: ``Bone Animation``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mcal

Usage Example::

    from scfile import formats

    with formats.McalDecoder("animations.mcal") as mcal:
        data = mcal.decode()
"""

from .decoder import McalDecoder


__all__ = ("McalDecoder",)
