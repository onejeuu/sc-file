"""
Base class for file format encoders.

Defines the contract for serializing structured content into binary data.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from io import BytesIO
from typing import ClassVar, Optional, Self, cast

from scfile.enums import HandlerState
from scfile.io.base import OutputStream, StructWriter
from scfile.options import Options
from scfile.types import SourceLike

from .base import Handler
from scfile.structures.content import BaseContent


type ContentTransform[ContentType] = Callable[[ContentType], ContentType]
type EncoderTransforms[ContentType] = Sequence[ContentTransform[ContentType]]


class Encoder[
    ContentType: BaseContent,
    WriterType: StructWriter = StructWriter,
](Handler[WriterType], ABC):
    """
    Base class for encoding structured content into binary data.

    Subclasses define the format-specific serialization logic.
    """

    content_type: ClassVar[type[BaseContent]]
    """Content type accepted by encoder."""

    io_factory = cast(type[WriterType], StructWriter)
    """Writer factory used to wrap the output stream."""

    transforms: Sequence[ContentTransform[ContentType]] = ()
    """Format-specific content transforms applied before serialization."""

    def __init__(
        self,
        data: ContentType,
        options: Optional[Options] = None,
        output: Optional[OutputStream] = None,
    ):
        """
        Initialize encoder.

        Args:
            data: Structured content to encode.
            options (optional): Shared handlers options.
            output (optional): File path or binary IO stream. Defaults to in-memory buffer.

        Note:
            Data is not written during initialization.
            Call :meth:`encode` to perform the actual serialization.
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
        Runs encoding pipeline.

        Args:
            transforms: Override the default transforms for this call.

        Returns:
            Self (chaining).
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
        """Encode if needed and return serialized bytes."""

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
        Write encoded data to file by name.

        Args:
            path: Output file path.
            close: Close encoder after writing.
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
        Write encoded data to file by stem. Format suffix appended.

        Args:
            path: Output file path.
            close: Close encoder after writing.
        """

        self.save(
            path=f"{path}{self.suffix()}",
            close=close,
        )

    def _prelude(self) -> None:
        """Hook called before transforms, signature and serialization."""
        pass

    def _transform(
        self,
        transforms: Optional[EncoderTransforms[ContentType]] = None,
    ) -> None:
        """Apply format-specific content transforms."""

        if transforms is None:
            transforms = self.transforms

        for transform in transforms:
            self.data = transform(self.data)

    def _add_signature(self) -> None:
        """Write the format signature to the output stream."""

        if self.signature:
            self.io.write(self.signature)

    @abstractmethod
    def _serialize(self) -> None:
        """Write ``self.data`` to the output stream. Called by :meth:`encode`."""
        ...
