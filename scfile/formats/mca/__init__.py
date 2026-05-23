"""
MCA Format.

:Type: Region Encoder
:Name: Minecraft Chunks Anvil
:Wiki: `<https://minecraft.wiki/w/Anvil_file_format>`_
:Co-authors: `<https://github.com/DeTTK>`_

Example::

    from scfile import formats

    with formats.mca.McaEncoder(data) as mca:
        mca.encode().save("r.0.0.mca")
"""

from .encoder import McaEncoder


__all__ = ("McaEncoder",)
