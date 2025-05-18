"""
Extends standard IO streams with struct-based I/O support.
"""

import io
import struct
from pathlib import Path

from scfile import exceptions as exc

from .base import StructIO


class StructBytesIO(io.BytesIO, StructIO):
    pass


class StructFileIO(io.FileIO, StructIO):
    @property
    def path(self) -> Path:
        return Path(str(self.name))

    @property
    def filesize(self) -> int:
        return self.path.stat().st_size

    def is_eof(self) -> bool:
        return self.filesize <= self.tell()

    def unpack(self, fmt: str):
        try:
            return super().unpack(fmt)

        except struct.error as err:
            raise exc.FileStructureInvalid(self.path, self.tell()) from err
