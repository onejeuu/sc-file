"""
Base class for file format decoders.

Defines the contract for parsing binary data into structured content.
"""

from abc import ABC, abstractmethod
from typing import ClassVar, Optional, cast

from scfile import exceptions
from scfile.enums import HandlerState
from scfile.io.base import IOStream, OutputStream, StructReader, StructWriter
from scfile.options import Options
from scfile.structures.content import BaseContent

from .base import Handler
from .encoder import Encoder


class Decoder[
    ContentType: BaseContent,
    ReaderType: StructReader = StructReader,
](Handler[ReaderType], ABC):
    """
    Base class for decoding binary data into structured content.

    Subclasses define format-specific parsing logic.
    """

    content_type: ClassVar[type[BaseContent]]
    """Factory for decoded content."""

    io_factory = cast(type[ReaderType], StructReader)
    """Reader factory used to wrap the source stream."""

    standalone: ClassVar[bool] = True
    """Whether decoded content can be converted without a related asset."""

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

        self.data = cast(ContentType, self.content_type())
        super().__init__(
            io=self.io_factory(
                stream,
                order=self.order,
            ),
            options=options if options is not None else Options(),
        )

    def decode(self) -> ContentType:
        """Decode source data once and return parsed content."""

        if self.state is HandlerState.SUCCEEDED:
            return self.data

        self._validate_state("decode", HandlerState.INITIAL)

        self._state = HandlerState.RUNNING

        try:
            self._verify_filesize()
            self._prelude()
            self._verify_signature()
            self._parse()

        except BaseException:
            self._state = HandlerState.FAILED
            raise

        self._state = HandlerState.SUCCEEDED
        return self.data

    def convert_to[WriterType: StructWriter](
        self,
        encoder: type[Encoder[ContentType, WriterType]],
        options: Optional[Options] = None,
        output: Optional[OutputStream] = None,
    ) -> Encoder[ContentType, WriterType]:
        """
        Decode and convert to given encoder format.

        Args:
            encoder: Encoder class to use for conversion.
            options (optional): Shared handlers options.
            output (optional): File path or binary IO stream. Defaults to in-memory buffer.

        Returns:
            Open encoder instance.
        """

        options = options or self.options
        data = self.decode()

        return encoder(data=data, options=options, output=output)

    def convert[WriterType: StructWriter](
        self,
        encoder: type[Encoder[ContentType, WriterType]],
        options: Optional[Options] = None,
    ) -> bytes:
        """
        Decode and convert to given encoder format.

        Args:
            encoder: Encoder class to use for conversion.
            options (optional): Shared handlers options.

        Returns:
            Encoded file content as bytes.
        """

        with self.convert_to(encoder, options=options) as enc:
            return enc.to_bytes()

    def _prelude(self) -> None:
        """Hook called before signature and parsing."""
        pass

    def _verify_filesize(self) -> None:
        """Verify source contains data before format-specific parsing."""

        if self.io.size() == 0:
            raise exceptions.EmptyFileError(self.location)

    def _verify_signature(self) -> None:
        """
        Validate file signature.

        Raises:
            `SignatureMismatchError` on failure.
        """

        if self.signature:
            offset = self.io.tell()
            read = self.io.read(len(self.signature))

            if read != self.signature:
                raise exceptions.SignatureMismatchError(
                    actual=read,
                    expected=self.signature,
                    location=self.location,
                    offset=offset,
                )

    @abstractmethod
    def _parse(self) -> None:
        """Parse file content into ``self.data``. Called by :meth:`decode`."""
        ...
