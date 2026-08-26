"""
EFKMODEL Format.

:Name: **Effekseer Model**
:Handler: :class:`~scfile.formats.efkmodel.decoder.EfkmodelDecoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.efkmodel``
:Support: ``⚠️ PARTIAL``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Colors``
:Wiki: https://sc-file.rtfd.io/page/formats.html#efkmodel

Usage Example::

    from scfile import formats

    with formats.EfkmodelDecoder("model.efkmodel") as efkmodel:
        data = efkmodel.decode()
"""

from .decoder import EfkmodelDecoder


__all__ = ("EfkmodelDecoder",)
