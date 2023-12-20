from abc import ABC, abstractmethod, abstractproperty
from io import BytesIO
from pathlib import Path
from typing import Type

from scfile import exceptions as exc
from scfile.consts import PathLike
from scfile.enums import ByteOrder
from scfile.enums import StructFormat as Format
from scfile.files.output.base import BaseOutputFile, OutputData
from scfile.reader import BinaryReader


class BaseSourceFile(ABC):
    DEFAULT_VALIDATE = True

    def __init__(self, path: PathLike, validate_signature: bool = DEFAULT_VALIDATE):
        self.path = Path(path)
        self.validate = validate_signature

        self.reader = BinaryReader(self.path, self.order)
        self.buffer = BytesIO()

        self.check_filesize()
        self.check_signature()

    output: Type[BaseOutputFile]
    """Output file model."""

    signature: int
    """Signature of source file. For example: `0x38383431`."""

    order: ByteOrder = BinaryReader.DEFAULT_BYTEORDER
    """Reader bytes order format."""

    def convert(self) -> bytes:
        """Convert source file. Return output file bytes."""
        self.parse()
        self.output(self.path, self.data, self.buffer).create()
        return self.result

    @abstractproperty
    def data(self) -> OutputData:
        """Return output data."""
        ...

    @abstractmethod
    def parse(self) -> None:
        """Parse source file."""
        ...

    @property
    def result(self) -> bytes:
        """Result bytes of conversion."""
        return self.buffer.getvalue()

    @property
    def filename(self) -> str:
        """Filename of source file."""
        return self.path.stem

    @property
    def filesize(self) -> int:
        """Size of source file."""
        return self.path.stat().st_size

    def check_filesize(self) -> None:
        """Check if file size is valid."""
        if self.filesize < len(str(self.signature)):
            raise exc.FileIsEmpty(self.path)

    def validate_signature(self, signature: int) -> bool:
        """Validate signature of source file."""
        return signature == self.signature

    def check_signature(self) -> None:
        """Check if signature of source file is valid."""
        signature = self.reader.readbin(Format.U32, ByteOrder.LITTLE)

        if self.validate and not self.validate_signature(signature):
            raise exc.InvalidSignature(self.path, signature, self.signature)

    def close(self):
        self.reader.close()
        self.buffer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __str__(self):
        return f"<{self.__class__.__name__}> path='{self.path.as_posix()}' "
