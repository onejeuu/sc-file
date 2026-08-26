"""
MCSA Format.

:Name: **Scene Assets (Legacy)**
:Handler: :class:`~scfile.formats.mcsa.decoder.McsaDecoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.mcsa``
:Support: ``✅ FULL``
:Versions: ``7.0``, ``8.0``, ``9.0``, ``10.0``, ``11.0``, ``12.0``, ``15.0``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``
:Wiki: https://sc-file.rtfd.io/page/formats.html#mcsa

Usage Example::

    from scfile import formats

    with formats.McsaDecoder("model.mcsa") as mcsa:
        data = mcsa.decode()
"""

from . import versions
from .decoder import McsaDecoder


__all__ = (
    "McsaDecoder",
    "versions",
)
