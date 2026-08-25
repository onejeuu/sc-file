"""Source decoding contract."""

from abc import ABC, abstractmethod
from typing import ClassVar, Optional, cast

from scfile import exceptions
from scfile.content import BaseContent
from scfile.enums import HandlerState
from scfile.io.base import IOStream, OutputStream, StructReader, StructWriter
from scfile.options import Options

from .base import Handler
from .encoder import Encoder


class Decoder[
    ContentType: BaseContent,
    ReaderType: StructReader = StructReader,
](Handler[ReaderType], ABC):
    """
    Base class for decoding binary sources into structured content.

    Subclasses define format-specific parsing logic.
    """

    content_type: ClassVar[type[BaseContent]]
    """Content type created by this decoder."""

    io_factory = cast(type[ReaderType], StructReader)
    """Structured reader class used to open source input."""

    standalone: ClassVar[bool] = True
    """Whether the source can be converted without related assets."""

    def __init__(
        self,
        stream: IOStream,
        options: Optional[Options] = None,
    ):
        """
        Initialize decoder.

        Args:
            stream: Source file path, source bytes, or binary stream.
            options (optional): Options used by this decoder.

        Note:
            Parsing is deferred until :meth:`decode` is called.
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
        """Decode source data and return content."""

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
        Decode source data and return a target encoder.

        Args:
            encoder: Encoder class for the target format.
            options (optional): Options for the target encoder. Defaults to decoder options.
            output (optional): Output file path or binary stream. Defaults to in-memory buffer.

        Returns:
            Open target encoder with decoded content.
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
        Decode source data and return encoded bytes.

        Args:
            encoder: Encoder class for the target format.
            options (optional): Options for the target encoder. Defaults to decoder options.

        Returns:
            Encoded bytes.
        """

        with self.convert_to(encoder, options=options) as enc:
            return enc.to_bytes()

    def _prelude(self) -> None:
        """Run before signature verification and source parsing."""
        pass

    def _verify_filesize(self) -> None:
        """Verify source data is not empty before parsing."""

        if self.io.size() == 0:
            raise exceptions.EmptyFileError(self.location)

    def _verify_signature(self) -> None:
        """
        Verify source signature.

        Raises:
            SignatureMismatchError: The expected signature does not match.
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
        """Parse format data into ``self.data``."""
        ...
