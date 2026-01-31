"""
Core module. It defines base classes and their interaction interface.
"""

from . import base, decoder, encoder, types, context, io
from .base import BaseFile
from .decoder import FileDecoder
from .encoder import FileEncoder
from .context.options import UserOptions
from .context.content import FileContent, ModelContent, TextureContent, ImageContent, TextureArrayContent, NbtContent


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
    "UserOptions",
    "FileContent",
    "ModelContent",
    "TextureContent",
    "ImageContent",
    "TextureArrayContent",
    "NbtContent",
)
