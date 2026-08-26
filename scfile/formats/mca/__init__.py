"""
MCA Format.

:Name: **Minecraft Chunks Anvil**
:Handler: :class:`~scfile.formats.mca.encoder.McaEncoder`
:Content: :class:`~scfile.content.base.RegionContent`
:Suffix: ``.mca``
:Support: ``🧪 EXPERIMENTAL``
:Versions: Minecraft Java ``1.12.2+`` (Anvil ``1343``)
:Contents: ``Blocks``, ``Biomes``
:Co-authors: ``DeTTK``, ``BoJIwEbNuK7``
:Wiki: https://minecraft.wiki/w/Anvil_file_format

Usage Example::

    from scfile import formats

    with formats.McaEncoder(data) as mca:
        mca.save("r.0.0.mca")
"""

from .encoder import McaEncoder


__all__ = ("McaEncoder",)
