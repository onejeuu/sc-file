"""
Base class for file format decoders.

Defines the contract for parsing binary data into structured content.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Optional, Type, TypeVar, cast

from scfile import exceptions
from scfile.io.base import IOStream, StructReader

from .base import BaseFile
from .content import BaseContent, ContentType
from .encoder import FileEncoder
from .options import Options


EncoderType = TypeVar("EncoderType", bound=FileEncoder[Any, Any])
ReaderType = TypeVar("ReaderType", bound=StructReader, default=StructReader)


class FileDecoder(BaseFile[ReaderType], Generic[ContentType, ReaderType], ABC):
    """
    Base class for decoding binary data into structured content.

    Subclasses define format-specific parsing logic.
    """

    content_factory: ClassVar[type[BaseContent]]
    """Factory for decoded content."""

    io_factory = cast(type[ReaderType], StructReader)

    convertible: bool = True
    """Allow direct conversion into compatible output formats."""

    def __init__(
        self,
        stream: IOStream,
        options: Optional[Options] = None,
    ):
        """
        Initialize decoder.

        Args:
            stream: Source input to decode. File path, bytes, or binary IO stream.
            options (optional): Shared handlers options.

        Note:
            The file is not parsed during initialization.
            Call :meth:`decode` to perform the actual parsing.
        """

        self.data = cast(ContentType, self.content_factory())
        self.options: Options = options or Options()

        super().__init__(stream=stream, mode="rb")

    def decode(self) -> ContentType:
        """
        Runs decoding pipeline.

        Args:
            seek: Reset stream position to the beginning after parsing.

        Returns:
            Parsed content data.
        """

        self.prelude()
        self.validate_signature()
        self.parse()
        return self.data

    def convert_to(
        self,
        encoder: Type[EncoderType],
        options: Optional[Options] = None,
        output: Optional[IOStream] = None,
    ) -> EncoderType:
        """
        Decode and convert to given encoder format.

        Args:
            encoder: Encoder class to use for conversion.
            options (optional): Shared handlers options.
            output (optional): File path or binary IO stream. Defaults to in-memory buffer.

        Returns:
            Clear encoder instance.
        """

        options = options or self.options
        data = self.decode()

        return encoder(data=data, options=options, output=output)

    def convert(
        self,
        encoder: Type[EncoderType],
        options: Optional[Options] = None,
        output: Optional[IOStream] = None,
    ) -> bytes:
        """
        Decode and convert to given encoder format.

        Args:
            encoder: Encoder class to use for conversion.
            options (optional): Shared handlers options.
            output (optional): File path or binary IO stream. Defaults to in-memory buffer.

        Returns:
            Encoded file content as bytes.
        """

        with self.convert_to(encoder, options=options, output=output) as enc:
            return enc.getvalue()

    def prelude(self) -> None:
        """Hook called before signature and parsing."""
        pass

    @abstractmethod
    def parse(self) -> None:
        """Parse file content into ``self.data``. Called by :meth:`decode`."""
        ...

    def validate_signature(self) -> None:
        """
        Validate file signature.

        Raises:
            `EmptyFileError` or `SignatureMismatchError` on failure.
        """

        if self.io.size() <= len(self.signature or bytes()):
            raise exceptions.EmptyFileError(self.location)

        if self.signature:
            offset = self.io.tell()
            read = self.io.read(len(self.signature))

            if read != self.signature:
                raise exceptions.SignatureMismatchError(
                    read,
                    self.signature,
                    location=self.location,
                    offset=offset,
                )
