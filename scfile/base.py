from abc import ABC, abstractmethod, abstractproperty
from io import BufferedReader, BytesIO
from pathlib import Path

from scfile.exceptions import InvalidSignature
from scfile.reader import BinaryFileReader


class BaseInputFile(ABC):
    def __init__(self, buffer: BufferedReader, validate: bool = True):
        self.validate = validate
        self.filename = Path(buffer.name).stem
        self.reader = BinaryFileReader(buffer=buffer)
        self.buffer = BytesIO()

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

    def validate_signature(self, signature: int) -> bool:
        return signature == self.signature

    def check_signature(self) -> None:
        signature = self.reader.udword()

        if self.validate and not self.validate_signature(signature):
            raise InvalidSignature()


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
