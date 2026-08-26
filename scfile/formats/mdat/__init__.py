"""
MDAT Format.

:Name: **World Region Cache**
:Handler: :class:`~scfile.formats.mdat.decoder.MdatDecoder`
:Content: :class:`~scfile.content.base.RegionContent`
:Suffix: ``.mdat``
:Support: ``🧪 EXPERIMENTAL``
:Versions: ``5.0``
:Contents: ``Blocks``, ``Metadata``, ``Lighting``, ``Biomes``
:Co-authors: ``DeTTK``, ``BoJIwEbNuK7``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mdat

Usage Example::

    from scfile import formats

    with formats.MdatDecoder("reg.0.0.mdat") as mdat:
        data = mdat.decode()
"""

from .decoder import MdatDecoder


__all__ = ("MdatDecoder",)
