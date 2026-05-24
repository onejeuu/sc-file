"""
MS3D Format.

:Name: **MilkShape 3D**
:Type: **🧊 Model Encoder**
:Wiki: `<https://developer.valvesoftware.com/wiki/MilkShape_3D>`_
:Suffix: ``.ms3d``
:Support: ``⚠️ Partial``
:Features: ``Geometry``, ``Skeleton``

Example::

    from scfile import formats

    with formats.ms3d.Ms3dEncoder(data) as ms3d:
        ms3d.encode().save("output.ms3d")
"""

from . import exceptions
from .encoder import Ms3dEncoder


__all__ = (
    "Ms3dEncoder",
    "exceptions",
)
