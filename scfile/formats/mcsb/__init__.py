"""
MCSB Format.

:Name: **Scene Bundle**
:Handler: :class:`~scfile.formats.mcsb.decoder.McsbDecoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.mcsb``
:Support: ``✅ FULL``
:Versions: ``7.0``, ``8.0``, ``9.0``, ``10.0``, ``11.0``, ``12.0``, ``15.0``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mcsb

Usage Example::

    from scfile import formats

    with formats.McsbDecoder("model.mcsb") as mcsb:
        data = mcsb.decode()
"""

from .decoder import McsbDecoder


__all__ = ("McsbDecoder",)
