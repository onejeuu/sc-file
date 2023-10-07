from abc import ABC, abstractmethod, abstractclassmethod
from io import BytesIO
from pathlib import Path

from scfile import exceptions as exc
from scfile.utils.reader import BinaryReader


class BaseSourceFile(ABC):
    DEFAULT_VALIDATE = True

    def __init__(
        self,
        reader: BinaryReader,
        validate: bool = DEFAULT_VALIDATE
    ):
        self.reader = reader
        self.buffer = BytesIO()

        self.validate = validate

        self._check_filesize()
        self._check_signature()

    signature: int
    """First 4 bytes in file."""

    @abstractmethod
    def convert(self) -> bytes:
        """Parsing and creating converted file bytes."""
        ...

    @abstractmethod
    def _parse(self) -> None:
        """Parsing encrypted file."""
        ...

    @property
    def path(self) -> Path:
        return self.reader.path

    @property
    def result(self) -> bytes:
        """Returns buffer bytes."""
        return self.buffer.getvalue()

    @property
    def filename(self) -> str:
        return self.path.stem

    @property
    def filesize(self) -> int:
        return self.path.stat().st_size

    def validate_signature(self, signature: int) -> bool:
        return signature == self.signature

    def _check_filesize(self) -> None:
        if self.filesize <= 0:
            raise exc.FileIsEmpty()

    def _check_signature(self) -> None:
        signature = self.reader.u32()

        if self.validate and not self.validate_signature(signature):
            raise exc.InvalidSignature(
                (
                    f"File '{self.path.as_posix()}' has invalid signature "
                    f"({hex(signature)} != {hex(self.signature)})"
                )
            )

    def __str__(self):
        return (
            f"<{self.__class__.__name__}> "
            f"signature='{self.signature}'"
            f"path='{self.path.as_posix()}' "
            f"pos={self.reader.tell()}"
        )
