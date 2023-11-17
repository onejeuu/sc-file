from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

from scfile import exceptions as exc
from scfile.files.output.base import BaseOutputFile
from scfile.reader import BinaryReader, ByteOrder


class BaseSourceFile(ABC):
    DEFAULT_VALIDATE = True

    def __init__(
        self,
        reader: BinaryReader,
        validate: bool = DEFAULT_VALIDATE
    ):
        self.reader = reader
        self.reader.order = self.order

        self.validate = validate

        self.buffer = BytesIO()

        self._check_filesize()
        self._check_signature()

    signature: int
    """Signature of source file. For example: `0x38383431`."""

    order: ByteOrder = BinaryReader.DEFAULT_BYTEORDER
    """Binary reader bytes order format."""

    def convert(self) -> bytes:
        """Convert source file. Return output file bytes."""
        self._parse()
        self._output().create()
        return self.result

    @abstractmethod
    def _output(self) -> BaseOutputFile:
        """Return default output file object."""
        ...

    @abstractmethod
    def _parse(self) -> None:
        """Parse source file."""
        ...

    @property
    def result(self) -> bytes:
        """Result bytes of conversion."""
        return self.buffer.getvalue()

    @property
    def path(self) -> Path:
        """Path of source file."""
        return self.reader.path

    @property
    def filename(self) -> str:
        """Filename of source file."""
        return self.path.stem

    @property
    def filesize(self) -> int:
        """Size of source file."""
        return self.path.stat().st_size

    def _check_filesize(self) -> None:
        """Check if file size is valid."""
        if self.filesize <= 0:
            raise exc.FileIsEmpty(self.path)

    def validate_signature(self, signature: int) -> bool:
        """Validate signature of source file."""
        return signature == self.signature

    def _read_signature(self) -> int:
        """Read signature from source file."""
        self.reader.order = ByteOrder.STANDARD
        signature = self.reader.u32()
        self.reader.order = self.order

        return signature

    def _check_signature(self) -> None:
        """Check if signature of source file is valid."""
        signature = self._read_signature()

        if self.validate and not self.validate_signature(signature):
            raise exc.InvalidSignature(self.path, signature, self.signature)

    def __str__(self):
        return (
            f"<{self.__class__.__name__}> "
            f"signature='{self.signature}'"
            f"path='{self.path.as_posix()}' "
            f"pos={self.reader.tell()}"
        )
