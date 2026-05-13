"""
Core module. It defines base classes and their interaction interface.
"""

from . import base, context, decoder, encoder, io
from .base import BaseFile
from .context.content import FileContent, ImageContent, ModelContent, NbtContent, TextureArrayContent, TextureContent
from .context.options import UserOptions
from .decoder import FileDecoder
from .encoder import FileEncoder


__all__ = (
    "base",
    "decoder",
    "encoder",
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
