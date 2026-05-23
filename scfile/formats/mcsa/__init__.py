"""
MCSA Format.

:Type: Model Decoder
:Name: Scene Assets
:Wiki: `<https://sc-file.rtfd.io/en/latest/formats.html#mcsa-scene-assets-mcsa-bt>`_

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
