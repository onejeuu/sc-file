import warnings

from .texture import TextureType


warnings.warn(
    "Module 'scfile.structures.types' is deprecated and will be removed in the next minor version. "
    "Please import from 'scfile.structures.texture' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["TextureType"]
__deprecated__ = True
