import io
from pathlib import Path

from scfile.io.base import BinaryIO


class BinaryBytesIO(io.BytesIO, BinaryIO):
    pass


class BinaryFileIO(io.FileIO, BinaryIO):
    @property
    def path(self) -> Path:
        return Path(str(self.name))
