"""
Core module. It defines base classes and their interaction interface.
"""

from . import base, decoder, encoder, types, context, io
from .base import BaseFile
from .decoder import FileDecoder
from .encoder import FileEncoder


__all__ = (
    "base",
    "decoder",
    "encoder",
    "types",
    "context",
    "io",
    "BaseFile",
    "FileDecoder",
    "FileEncoder",
)
