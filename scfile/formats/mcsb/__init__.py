"""
MCSB Format.

:Type: Model Decoder
:Name: Scene Bundle
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#mcsb-scene-bundle-mcsa-bt>`_

Example::

    from scfile import formats

    with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
        data = mcsb.decode()
"""

from .decoder import McsbDecoder


__all__ = ("McsbDecoder",)
