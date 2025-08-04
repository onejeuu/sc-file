"""
Base class for file decoder (parsing).
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, Type

from scfile import exceptions
from scfile.enums import FileMode
from scfile.types import PathLike

from .base import BaseFile
from .context import UserOptions
from .encoder import FileEncoder
from .io import StructFileIO
from .types import Content


class FileDecoder(BaseFile, StructFileIO, Generic[Content], ABC):
    """Base class for decoding file content into structured data objects."""

    mode: str = FileMode.READ

    _content: type[Content]

    def __init__(self, file: PathLike, options: Optional[UserOptions] = None):
        """Initialize file decoder with source file and options.

        Arguments:
            file: Path to file that will be decoded. Can be any `path-like` object.
            options (optional): User provided options. If None, default `UserOptions` will be used.

        Initialized:
            file (`PathLike`): The input file path.
            options (`UserOptions`): Decoding options (default or user provided).
            data (`Generic[Content]`): Empty instance of content type for storing decoded data.

        Note:
            Actual decoding doesn't happen during initialization.
            Call `decode()` to perform parsing process.
        """

        self.file = file
        self.options: UserOptions = options or UserOptions()
        self.data: Content = self._content()

        super().__init__(file=self.file, mode=self.mode)

    def decode(self, seek: bool = True) -> Content:
        """Decode file: prepare, validate signature, parse. Returns parsed data."""
        self.prepare()
        self.validate_signature()
        self.parse()
        if seek:
            self.seek(0)
        return self.data

    def convert_to(
        self,
        encoder: Type[FileEncoder[Content]],
        options: Optional[UserOptions] = None,
    ) -> FileEncoder[Content]:
        """Decode and convert to encoder. Returns encoder with open buffer (must be closed)."""
        options = options or self.options
        data = self.decode()
        enc = encoder(data, options)
        enc.encode()
        return enc

    def convert(
        self,
        encoder: type[FileEncoder[Content]],
        options: Optional[UserOptions] = None,
    ) -> bytes:
        """Decode, convert to encoder and return bytes. Closes encoder automatically."""
        options = options or self.options
        enc = self.convert_to(encoder, options)
        content = enc.getvalue()
        enc.close()
        return content

    def prepare(self) -> None:
        """Perform file preparation before parsing. *(e.g. skip bytes)*."""
        pass

    @abstractmethod
    def parse(self) -> None:
        """Parse file content into `self.data`."""
        pass

    def validate_signature(self) -> None:
        """Validate file signature. Raises `EmptyFileError` or `InvalidSignatureError` on failure."""
        if self.filesize <= len(self.signature or bytes()):
            raise exceptions.EmptyFileError(self.path)

        if self.signature:
            read = self.read(len(self.signature))

            if read != self.signature:
                raise exceptions.InvalidSignatureError(self.path, read, self.signature)

    def close(self) -> None:
        """Close file buffer. Same as `FileIO.close()`."""
        super().close()
