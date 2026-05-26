"""
Base class for file format decoders.

Defines the contract for parsing binary data into structured content.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar

from scfile import exceptions

from .base import BaseFile, IOStream
from .content import ContentType
from .encoder import FileEncoder
from .options import Options


EncoderType = TypeVar("EncoderType", bound=FileEncoder)


class FileDecoder(BaseFile, Generic[ContentType], ABC):
    """
    Base class for decoding binary data into structured content.

    Subclasses define format-specific parsing logic.
    """

    _content: type[ContentType]

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

        self.data: ContentType = self._content()
        self.options: Options = options or Options()

        super().__init__(stream=stream, mode="rb")

    def decode(
        self,
        seek: bool = True,
    ) -> ContentType:
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
        if seek:
            self.seek(0)
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
            `EmptyFileError` or `InvalidSignatureError` on failure.
        """

        if self.size() <= len(self.signature or bytes()):
            raise exceptions.EmptyFileError(self.location)

        if self.signature:
            read = self.read(len(self.signature))

            if read != self.signature:
                raise exceptions.InvalidSignatureError(self.location, read, self.signature)
