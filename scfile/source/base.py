from abc import ABC, abstractmethod, abstractproperty
from io import BufferedReader, BytesIO
from pathlib import Path

from scfile import exceptions as exc
from scfile.utils.reader import BinaryFileReader


class BaseSourceFile(ABC):
    DEFAULT_VALIDATE = True

    def __init__(
        self,
        buffer: BufferedReader,
        validate: bool = DEFAULT_VALIDATE
    ):
        self._path = Path(buffer.name)

        self.reader = BinaryFileReader(buffer=buffer)
        self.buffer = BytesIO()

        self.validate = validate

        self._check_filesize()
        self._check_signature()

    @abstractproperty
    def signature(self) -> int:
        """First 4 bytes in file."""
        ...

    @abstractmethod
    def convert(self) -> bytes:
        """Parsing and creating converted file bytes."""
        ...

    @abstractmethod
    def _parse(self) -> None:
        """Parsing encrypted file."""
        ...

    @property
    def result(self) -> bytes:
        """Returns buffer bytes."""
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
