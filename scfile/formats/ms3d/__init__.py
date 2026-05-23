"""
MS3D Format.

:Type: Model Encoder
:Name: MilkShape 3D
:Wiki: `<https://developer.valvesoftware.com/wiki/MilkShape_3D>`_
"""

from . import exceptions
from .encoder import Ms3dEncoder


__all__ = (
    "Ms3dEncoder",
    "exceptions",
)
