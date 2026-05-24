"""
EFKMODEL Format.

:Name: **Effekseer Model**
:Type: **🧊 Model Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#efkmodel-effekseer-model-efkmodel-bt>`_
:Suffix: ``.efkmodel``
:Support: ``⚠️ Partial``
:Features: ``Geometry``

Example::

    from scfile import formats

    with formats.efkmodel.EfkmodelDecoder("model.efkmodel") as efk:
        data = efk.decode()
"""

from .decoder import EfkmodelDecoder


__all__ = ("EfkmodelDecoder",)
