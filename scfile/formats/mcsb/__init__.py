"""
MCSB Format.

:Name: **Scene Bundle**
:Type: **🧊 Model Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mcsb-scene-bundle-mcsa-bt>`_
:Suffix: ``.mcsb``
:Support: ``✅ Full``
:Features: ``Geometry``, ``Skeleton``, ``Animation``

Example::

    from scfile import formats

    with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
        data = mcsb.decode()
"""

from .decoder import McsbDecoder


__all__ = ("McsbDecoder",)
