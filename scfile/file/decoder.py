from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional, TypeVar

from scfile.enums import ByteOrder, FileMode
from scfile.enums import StructFormat as F
from scfile.exceptions import InvalidSignature
from scfile.file.base import BaseFile
from scfile.file.data import FileData
from scfile.file.encoder import FileEncoder
from scfile.io.binary import BinaryFileIO
from scfile.types import PathLike


OPENER = TypeVar("OPENER", bound=BinaryFileIO)
DATA = TypeVar("DATA", bound=FileData)


class FileDecoder(BaseFile, Generic[OPENER, DATA], ABC):
    def __init__(self, path: PathLike):
        self._path = path

        self._file = self.opener(self.path, FileMode.READ)
        self._file.order = self.order

        self._data: Optional[DATA] = None

    @property
    def buffer(self):
        return self._file

    @property
    def f(self):
        return self._file

    @property
    def path(self) -> Path:
        return Path(self._path)

    @property
    def data(self):
        return self._data

    @property
    def order(self) -> ByteOrder:
        return ByteOrder.LITTLE

    @property
    def signature(self) -> Optional[int]:
        return None

    @property
    @abstractmethod
    def opener(self) -> type[OPENER]:
        pass

    @abstractmethod
    def create_data(self) -> DATA:
        pass

    @abstractmethod
    def parse(self):
        pass

    def decode(self) -> DATA:
        self.validate_signature()
        self.parse()
        self._data = self.create_data()
        return self._data

    def convert(self, encoder: type[FileEncoder[DATA]]) -> FileEncoder[DATA]:
        # TODO: Fix bad implementation

        data = self.decode()
        enc = encoder(data)
        enc.encode()
        return enc

    def validate_signature(self) -> None:
        if self.signature:
            readed = self.f.readb(F.U32, ByteOrder.LITTLE)

            if readed != self.signature:
                raise InvalidSignature(self.path, readed, self.signature)
