"""
EFKMODEL Format.

:Type: Model Decoder
:Name: Effekseer Model
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#efkmodel-effekseer-model-efkmodel-bt>`_

Example::

    from scfile import formats

    with formats.efkmodel.EfkmodelDecoder("model.efkmodel") as efk:
        data = efk.decode()
"""

from .decoder import EfkmodelDecoder


__all__ = ("EfkmodelDecoder",)
