"""
Structured binary I/O.
"""

from .structio import FileMode, IOStream, StructIO, StructReader, StructWriter


__all__ = (
    "StructIO",
    "StructReader",
    "StructWriter",
    "FileMode",
    "IOStream",
)
