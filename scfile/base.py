from abc import ABC, abstractmethod, abstractproperty
from io import BufferedReader, BytesIO
from pathlib import Path

from . import exceptions as exc
from .reader import BinaryFileReader


class BaseSourceFile(ABC):
    def __init__(self, buffer: BufferedReader, validate: bool = True):
        self._path = Path(buffer.name)

        self.reader = BinaryFileReader(buffer=buffer)
        self.buffer = BytesIO()

        self.validate = validate

        self._check_filesize()
        self._check_signature()

    @abstractproperty
    def signature(self) -> int:
        ...

    @abstractmethod
    def convert(self) -> bytes:
        ...

    @abstractmethod
    def _parse(self) -> bytes:
        ...

    @property
    def output(self) -> bytes:
        return self.buffer.getvalue()

    @property
    def filename(self) -> str:
        return self._path.stem

    @property
    def filesize(self) -> int:
        return self._path.stat().st_size

    def validate_signature(self, signature: int) -> bool:
        return signature == self.signature

    def _check_filesize(self) -> None:
        if self.filesize <= 0:
            raise exc.FileIsEmpty()

    def _check_signature(self) -> None:
        signature = self.reader.udword()

        if self.validate and not self.validate_signature(signature):
            raise exc.InvalidSignature()

    def __str__(self):
        return (
            f"<{self.__class__.__name__}> "
            f"path='{self._path.as_posix()}' pos={self.reader.tell()}"
        )


class BaseOutputFile(ABC):
    def __init__(self, buffer: BytesIO, filename: str = "file"):
        self.buffer = buffer
        self.filename = filename

    @abstractmethod
    def create(self) -> bytes:
        ...

    @property
    def output(self) -> bytes:
        return self.buffer.getvalue()

    def __str__(self):
        return f"<{self.__class__.__name__}> filename='{self.filename}'"
