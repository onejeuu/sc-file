"""
MCSA Format.

:Name: **Scene Assets**
:Type: **🧊 Model Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mcsa-scene-assets-mcsa-bt>`_
:Suffix: ``.mcsa``
:Support: ``✅ Full``
:Features: ``Geometry``, ``Skeleton``, ``Animation``

Example::

    from scfile import formats

    with formats.mcsa.McsaDecoder("model.mcsa") as mcsa:
        data = mcsa.decode()
"""

from . import exceptions, versions
from .decoder import McsaDecoder


__all__ = (
    "McsaDecoder",
    "exceptions",
    "versions",
)
