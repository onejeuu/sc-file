from abc import ABC, abstractmethod, abstractproperty
from io import BufferedReader, BytesIO
from pathlib import Path

from scfile import exceptions as exc
from scfile.reader import BinaryFileReader


class BaseInputFile(ABC):
    def __init__(self, buffer: BufferedReader, validate: bool = True):
        self._path = Path(buffer.name)

        self.reader = BinaryFileReader(buffer=buffer)
        self.buffer = BytesIO()

        self.validate = validate

        self.check_filesize()
        self.check_signature()

    @abstractproperty
    def signature(self) -> int:
        ...

    @abstractmethod
    def _convert(self) -> bytes:
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

    def check_signature(self) -> None:
        signature = self.reader.udword()

        if self.validate and not self.validate_signature(signature):
            raise exc.InvalidSignature()

    def check_filesize(self) -> None:
        if self.filesize <= 0:
            raise exc.FileIsEmpty()


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
