from abc import ABC, abstractmethod
from typing import Generic, Optional, Type

from scfile import exceptions

from .base import BaseFile, IOStream
from .content import ContentType
from .encoder import FileEncoder
from .options import UserOptions


class FileDecoder(BaseFile, Generic[ContentType], ABC):
    """Base class for decoding file content into structured data objects."""

    _content: type[ContentType]

    def __init__(
        self,
        stream: IOStream,
        options: Optional[UserOptions] = None,
    ):
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

        self.options: UserOptions = options or UserOptions()
        self.data: ContentType = self._content()

        super().__init__(stream=stream, mode="rb")

    def decode(
        self,
        seek: bool = True,
    ) -> ContentType:
        """Decode file: prelude, validate signature, parse. Returns parsed data."""
        self.prelude()
        self.validate_signature()
        self.parse()
        if seek:
            self.seek(0)
        return self.data

    def convert_to(
        self,
        encoder: Type[FileEncoder[ContentType]],
        options: Optional[UserOptions] = None,
    ) -> FileEncoder[ContentType]:
        """Decode and convert to encoder. Returns encoder with open buffer (must be closed)."""
        options = options or self.options
        data = self.decode()
        enc = encoder(data, options)
        enc.encode()
        return enc

    def convert(
        self,
        encoder: type[FileEncoder[ContentType]],
        options: Optional[UserOptions] = None,
    ) -> bytes:
        """Decode, convert to encoder and return bytes. Closes encoder automatically."""
        options = options or self.options
        enc = self.convert_to(encoder, options)
        content = enc.getvalue()
        enc.close()
        return content

    def prelude(self) -> None:
        """Runs before file parsing."""
        pass

    @abstractmethod
    def parse(self) -> None:
        """Parse file content into `self.data`."""
        pass

    def validate_signature(self) -> None:
        """Validate file signature. Raises `EmptyFileError` or `InvalidSignatureError` on failure."""
        if self.size <= len(self.signature or bytes()):
            raise exceptions.EmptyFileError(self.location)

        if self.signature:
            read = self.read(len(self.signature))

            if read != self.signature:
                raise exceptions.InvalidSignatureError(self.location, read, self.signature)

    def close(self) -> None:
        """Close file buffer. Same as `FileIO.close()`."""
        super().close()
