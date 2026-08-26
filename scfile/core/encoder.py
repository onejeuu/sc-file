"""Content encoding contract."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from io import BytesIO
from typing import ClassVar, Optional, Self, cast

from scfile.content import BaseContent
from scfile.enums import HandlerState
from scfile.io.base import OutputStream, StructWriter
from scfile.options import Options
from scfile.types import SourceLike

from .base import Handler


type ContentTransform[ContentType] = Callable[[ContentType], ContentType]
"""Function that transforms content before encoding."""

type EncoderTransforms[ContentType] = Sequence[ContentTransform[ContentType]]
"""Ordered content transforms applied by an encoder."""


class Encoder[
    ContentType: BaseContent,
    WriterType: StructWriter = StructWriter,
](Handler[WriterType], ABC):
    """Content encoder base class."""

    content_type: ClassVar[type[BaseContent]]
    """Type of content accepted by this encoder."""

    io_factory = cast(type[WriterType], StructWriter)
    """Writer class used to open output data."""

    transforms: Sequence[ContentTransform[ContentType]] = ()
    """Default content transforms applied before encoding."""

    def __init__(
        self,
        data: ContentType,
        options: Optional[Options] = None,
        output: Optional[OutputStream] = None,
    ):
        """
        Initialize encoder.

        Args:
            data: Content to encode.
            options (optional): Options used by this encoder.
            output (optional): Output file path or binary stream. Defaults to in-memory buffer.

        Note:
            Serialization is deferred until :meth:`encode` or :meth:`to_bytes` is called.
        """

        self.data: ContentType = data
        super().__init__(
            io=self.io_factory(
                output if output is not None else BytesIO(),
                order=self.order,
            ),
            options=options if options is not None else Options(),
        )

    def encode(
        self,
        transforms: Optional[EncoderTransforms[ContentType]] = None,
    ) -> Self:
        """
        Serialize content to output.

        Args:
            transforms: Content transforms used instead of the defaults.

        Returns:
            This encoder.
        """

        self._validate_state("encode", HandlerState.INITIAL)

        self._state = HandlerState.RUNNING

        try:
            self._prelude()
            self._transform(transforms=transforms)
            self._add_signature()
            self._serialize()

        except BaseException:
            self._state = HandlerState.FAILED
            raise

        self._state = HandlerState.SUCCEEDED
        return self

    def to_bytes(self) -> bytes:
        """Encode content when needed and return bytes."""

        if self.state is HandlerState.INITIAL:
            self.encode()

        self._validate_state("read encoded data", HandlerState.SUCCEEDED)
        return self.io.to_bytes()

    def save(
        self,
        path: SourceLike,
        *,
        close: bool = True,
    ) -> None:
        """
        Write encoded bytes to an output file path.

        Args:
            path: Exact output file path.
            close: Whether to close this encoder after writing.
        """

        try:
            data = self.to_bytes()

            with open(path, "wb") as fp:
                fp.write(data)

        finally:
            if close:
                self.close()

    def export(
        self,
        path: SourceLike,
        *,
        close: bool = True,
    ) -> None:
        """
        Write encoded bytes with the format suffix appended to ``path``.

        Args:
            path: Output path without the format suffix.
            close: Whether to close this encoder after writing.
        """

        self.save(
            path=f"{path}{self.suffix()}",
            close=close,
        )

    def _prelude(self) -> None:
        """Run before transforms and serialization."""
        pass

    def _transform(
        self,
        transforms: Optional[EncoderTransforms[ContentType]] = None,
    ) -> None:
        """Apply content transforms."""

        if transforms is None:
            transforms = self.transforms

        for transform in transforms:
            self.data = transform(self.data)

    def _add_signature(self) -> None:
        """Write the format signature."""

        if self.signature:
            self.io.write(self.signature)

    @abstractmethod
    def _serialize(self) -> None:
        """Serialize ``self.data`` to output."""
        ...
