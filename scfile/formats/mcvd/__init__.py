"""
MCVD Format.

:Name: **Trace Model** / **Animation Set**
:Handler: :class:`~scfile.formats.mcvd.decoder.McvdDecoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.mcvd``
:Support: ``✅ FULL``
:Versions: ``7.0``, ``8.0``, ``9.0``, ``10.0``, ``11.0``, ``12.0``, ``15.0``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mcvd

Usage Example::

    from scfile import formats

    with formats.McvdDecoder("file.mcvd") as mcvd:
        data = mcvd.decode()
"""

from .decoder import McvdDecoder


__all__ = ("McvdDecoder",)
