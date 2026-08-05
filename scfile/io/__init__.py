"""
Structured binary I/O.
"""

from .base import FileMode, IOStream, OutputStream, StructIO, StructReader, StructWriter


__all__ = (
    "StructIO",
    "StructReader",
    "StructWriter",
    "FileMode",
    "IOStream",
    "OutputStream",
)
