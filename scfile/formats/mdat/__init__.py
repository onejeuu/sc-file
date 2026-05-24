"""
MDAT Format.

:Name: **World Chunks Cache**
:Type: **🗺 Region Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mdat-world-chunks-cache>`_
:Co-authors: `<https://github.com/DeTTK>`_, BoJIwEbNuK7
:Suffix: ``.mdat``
:Support: ``🧪 Experimental``
:Features: ``Blocks``

Example::

    from scfile import formats

    with formats.mdat.MdatDecoder("reg.0.0.mdat") as mdat:
        data = mdat.decode()
"""

from .decoder import MdatDecoder


__all__ = ("MdatDecoder",)
