from abc import ABC, abstractmethod
from typing import Generic, Optional, Self, TypeVar

from scfile.enums import FileMode
from scfile.file.data import FileData
from scfile.io import BinaryBytesIO
from scfile.utils.types import PathLike

from .file import BaseFile


DATA = TypeVar("DATA", bound=FileData)


class FileEncoder(BaseFile, Generic[DATA], ABC):
    def __init__(self, data: DATA):
        self._buffer = BinaryBytesIO()
        self._data = data

    @property
    def buffer(self):
        return self._buffer

    @property
    def data(self):
        return self._data

    @property
    def b(self):
        """Bytes buffer abbreviation."""
        return self._buffer

    @property
    def magic(self) -> Optional[list[int]]:
        """Optional file magic value."""
        return None

    @property
    def content(self) -> bytes:
        """Buffer content bytes."""
        return self.b.getvalue()

    @abstractmethod
    def serialize(self) -> None:
        """Writing values from parsed data to buffer."""
        pass

    def encode(self) -> Self:
        """File encoding. Writing into buffer magic value and parsed data."""
        self.add_magic()
        self.serialize()
        return self

    def add_magic(self) -> None:
        """Writing into buffer magic value."""
        if self.magic:
            self.b.write(bytes(self.magic))

    def save_as(self, path: PathLike) -> None:
        """Saves content bytes to file at specified path. Buffer remains open."""
        with open(path, FileMode.WRITE) as fp:
            fp.write(self.content)

    def save(self, path: PathLike) -> None:
        """Saves content bytes to file at specified path. Buffer closes."""
        self.save_as(path)
        self.close()
