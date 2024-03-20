from abc import ABC, abstractmethod
from typing import Generic, Optional, Self, TypeVar

from scfile.enums import FileMode
from scfile.file.base import BaseFile
from scfile.file.data import FileData
from scfile.io.binary import BinaryBytesIO
from scfile.types import PathLike


DATA = TypeVar("DATA", bound=FileData)


class FileEncoder(BaseFile, Generic[DATA], ABC):
    def __init__(self, data: DATA):
        self._data = data
        self._buffer = BinaryBytesIO()

    @property
    def buffer(self):
        return self._buffer

    @property
    def b(self):
        return self._buffer

    @property
    def data(self):
        return self._data

    @property
    def magic(self) -> Optional[list[int]]:
        return None

    @property
    def result(self):
        return self.b.getvalue()

    @abstractmethod
    def serialize(self) -> None:
        pass

    def encode(self) -> Self:
        self.add_magic()
        self.serialize()
        return self

    def add_magic(self) -> None:
        if self.magic:
            self.b.write(bytes(self.magic))

    def save_as(self, path: PathLike) -> None:
        with open(path, FileMode.WRITE) as fp:
            fp.write(self.result)

    def save(self, path: PathLike) -> None:
        self.save_as(path)
        self.close()
