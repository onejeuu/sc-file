"""
Base class for file format encoders.

Defines the contract for serializing structured content into binary data.
"""

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Callable, ClassVar, Generic, Optional, Self, Sequence, TypeAlias, TypeVar, cast

from scfile.io.base import FileMode, IOStream, StructWriter
from scfile.structures.models import Feature, Features
from scfile.types import PathLike

from .base import BaseFile
from .content import BaseContent, ContentType, ModelContent
from .options import Options


ContentTransform: TypeAlias = Callable[[ContentType], ContentType]
EncoderTransforms: TypeAlias = Optional[Sequence[ContentTransform[ContentType]]]
WriterType = TypeVar("WriterType", bound=StructWriter, default=StructWriter)


class FileEncoder(BaseFile[WriterType], Generic[ContentType, WriterType], ABC):
    """
    Base class for encoding structured content into binary data.

    Subclasses define the format-specific serialization logic.
    """

    content_type: ClassVar[type[BaseContent]]
    """Content type accepted by encoder."""

    io_factory = cast(type[WriterType], StructWriter)

    features: ClassVar[Features] = ()
    """Optional content features supported by format."""

    transforms: Sequence[ContentTransform[ContentType]] = ()
    """Format-specific content transforms applied before serialization."""

    def __init__(
        self,
        data: ContentType,
        options: Optional[Options] = None,
        output: Optional[IOStream] = None,
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
        self.options: Options = options or Options()

        super().__init__(stream=output or BytesIO(), mode="wb+")

    def encode(
        self,
        transforms: EncoderTransforms = None,
    ) -> Self:
        """
        Runs encoding pipeline.

        Args:
            transforms: Override the default transforms for this call.

        Returns:
            Self (chaining).
        """

        self.prelude()
        self.transform(transforms=transforms)
        self.add_signature()
        self.serialize()
        return self

    def prelude(self) -> None:
        """Hook called before transforms, signature and serialization."""
        pass

    def transform(
        self,
        transforms: EncoderTransforms = None,
    ) -> None:
        """Apply format-specific content transforms."""

        transforms = transforms or self.transforms
        for transform in transforms:
            self.data = transform(self.data)

    def add_signature(self) -> None:
        """Write the format signature to the output stream."""

        if self.signature:
            self.io.write(self.signature)

    @abstractmethod
    def serialize(self) -> None:
        """Write ``self.data`` to the output stream. Called by :meth:`encode`."""
        ...

    def save(
        self,
        path: PathLike,
        mode: FileMode = "wb",
        close: bool = True,
    ) -> None:
        """
        Write encoded data to file by name.

        Args:
            path: Output file path.
            mode: File mode (binary).
            close: Close encoder after writing.
        """

        try:
            if self.io.size() == 0:
                self.encode()

            with open(path, mode=mode) as fp:
                fp.write(self.io.getvalue())

        finally:
            if close:
                self.close()

    def export(
        self,
        path: PathLike,
        mode: FileMode = "wb",
        close: bool = True,
    ) -> None:
        """
        Write encoded data to file by stem. Format suffix appended.

        Args:
            path: Output file path.
            mode: File mode (binary).
            close: Close encoder after writing.
        """

        self.save(
            path=f"{path}{self.suffix}",
            mode=mode,
            close=close,
        )

    def getvalue(self) -> bytes:
        if self.io.size() == 0:
            self.encode()
        return self.io.getvalue()

    def has(
        self: "FileEncoder[ModelContent, WriterType]",
        feature: Feature,
    ) -> bool:
        """Return whether input content contains a feature."""

        return self.data.has(feature)

    @classmethod
    def supports(
        cls,
        feature: Feature,
    ) -> bool:
        """Return whether output format supports a feature."""

        return any(member in cls.features for member in feature.members)

    def includes(
        self: "FileEncoder[ModelContent, WriterType]",
        feature: Feature,
    ) -> bool:
        """Return whether a feature will be serialized."""

        return self.options.includes(feature) and any(
            self.has(member)
            and self.supports(member)
            and all(self.includes(required) for required in member.requires)
            for member in feature.members
        )
