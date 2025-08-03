"""
Extends standard IO streams with struct-based I/O support.
"""

import io
import struct
from pathlib import Path

from scfile import exceptions

from .base import StructIO


class StructBytesIO(io.BytesIO, StructIO):
    """In-memory bytes buffer with structured binary operations."""

    pass


class StructFileIO(io.FileIO, StructIO):
    """File-based I/O with structured binary operations."""

    @property
    def path(self) -> Path:
        return Path(str(self.name))

    @property
    def filesize(self) -> int:
        return self.path.stat().st_size

    def is_eof(self) -> bool:
        return self.filesize <= self.tell()

    def _unpack(self, fmt: str):
        try:
            return super()._unpack(fmt)

        except struct.error as err:
            raise exceptions.InvalidStructureError(self.path, position=self.tell()) from err
