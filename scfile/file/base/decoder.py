from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional, TypeVar

from scfile.enums import ByteOrder, FileMode
from scfile.enums import StructFormat as F
from scfile.exceptions import FileSignatureInvalid
from scfile.file.data import FileData
from scfile.io import BinaryFileIO
from scfile.utils.types import PathLike

from .encoder import FileEncoder
from .file import BaseFile


OPENER = TypeVar("OPENER", bound=BinaryFileIO)
DATA = TypeVar("DATA", bound=FileData)


class FileDecoder(BaseFile, Generic[OPENER, DATA], ABC):
    def __init__(self, path: PathLike):
        self._path = path

        self._file = self.opener(self.path, self.mode)
        self._file.order = self.order

        self._data: Optional[DATA] = None

    @property
    def buffer(self):
        return self._file

    @property
    def data(self):
        return self._data

    @property
    def f(self):
        """File buffer abbreviation."""
        return self._file

    @property
    def path(self) -> Path:
        """Pathlib object to an open file."""
        return Path(self._path)

    @property
    def order(self) -> ByteOrder:
        """File reading default byte order."""
        return ByteOrder.LITTLE

    @property
    def signature(self) -> Optional[int]:
        """Optional file signature (4 bytes)."""
        return None

    @property
    def mode(self) -> str:
        """File opener mode."""
        return FileMode.READ

    @property
    @abstractmethod
    def opener(self) -> type[OPENER]:
        """Opener (reader) class for file."""
        pass

    @abstractmethod
    def create_data(self) -> DATA:
        """Creates an object with filled parsed data."""
        pass

    @abstractmethod
    def parse(self) -> None:
        """Reading file and entering values into data."""
        pass

    def decode(self) -> DATA:
        """File decoding. Signature validation, parsing and data creation."""
        self.validate_signature()
        self.parse()
        self._data = self.create_data()
        self.seek_to_start()
        return self._data

    def convert_to(self, encoder: type[FileEncoder[DATA]]) -> FileEncoder[DATA]:
        """Converting file into an object of passed encoder. Encoder has an open buffer."""
        data = self.decode()
        enc = encoder(data)
        enc.encode()
        return enc

    def convert(self, encoder: type[FileEncoder[DATA]]) -> bytes:
        """Converting file into content bytes of passed encoder."""
        enc = self.convert_to(encoder)
        content = enc.content
        enc.close()
        return content

    def read_signature(self) -> int:
        """Reading big-endian u32 (4 bytes) value."""
        return self.f.readb(F.U32, ByteOrder.BIG)

    def validate_signature(self) -> None:
        """Validates 4 bytes signature and throwing error in case of mismatch."""
        if self.signature:
            readed = self.read_signature()

            if readed != self.signature:
                raise FileSignatureInvalid(self.path, readed, self.signature)

    def seek_to_start(self) -> None:
        """Sets buffer position to start."""
        self.f.seek(0)
