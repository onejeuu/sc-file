import io
from pathlib import Path

from ._base import BinaryIO


class BinaryBytesIO(io.BytesIO, BinaryIO):
    pass


class BinaryFileIO(io.FileIO, BinaryIO):  # type: ignore
    @property
    def path(self) -> Path:
        return Path(str(self.name))
