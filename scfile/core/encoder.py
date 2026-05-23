"""
Base class for file format encoders.

Defines the contract for serializing structured content into binary data.
"""

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Generic, Optional, Self, TypeAlias

from scfile.structures.models import Flag
from scfile.structures.models.transforms import SceneTransform
from scfile.types import PathLike

from .base import BaseFile, IOStream
from .content import ContentType, ModelContent
from .options import Options


EncoderTransforms: TypeAlias = Optional[list[SceneTransform]]


class FileEncoder(BaseFile, Generic[ContentType], ABC):
    """
    Base class for serializing structured content into binary data.

    Subclasses define the format-specific serialization logic.
    """

    transforms: EncoderTransforms = None
    """Format-specific transforms applied to model data before serialization."""

    def __init__(
        self,
        data: ContentType,
        options: Optional[Options] = None,
        output: Optional[IOStream] = None,
    ):
        """
        Initialize encoder.

        Args:
            data: Content to encode.
            options: Optional settings for parsing.
            output: Optional destination. File path or binary IO stream. Defaults to in-memory buffer.

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
    ):
        """Apply format-specific transforms to model data."""

        transforms = transforms or self.transforms
        if transforms and isinstance(self.data, ModelContent):
            scene = self.data.scene
            for tr in transforms:
                scene = tr(scene)
            self.data.scene = scene

    def add_signature(self) -> None:
        """Write the format signature to the output stream."""

        if self.signature:
            self.write(self.signature)

    @abstractmethod
    def serialize(self) -> None:
        """Write ``self.data`` to the output stream. Called by :meth:`encode`."""
        ...

    def save_as(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """
        Write encoded data to file by name. Keeps encoder open.

        Args:
            path: Output file path.
            mode: File open mode.
        """

        with open(path, mode=mode) as fp:
            fp.write(self.getvalue())

    def export_as(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """
        Write encoded data to file by stem. Format suffix appended. Keeps the encoder open.

        Args:
            path: Output file path.
            mode: File open mode.
        """

        self.save_as(path=f"{path}{self.suffix}", mode=mode)

    def save(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """
        Write encoded data to file by name. Closes encoder.

        Args:
            path: Output file path.
            mode: File open mode.
        """

        self.save_as(path=path, mode=mode)
        self.close()

    def export(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """
        Write encoded data to file by stem. Format suffix appended. Closes encoder.

        Args:
            path: Output file path.
            mode: File open mode.
        """

        self.save(path=f"{path}{self.suffix}", mode=mode)
        self.close()

    @property
    def _skeleton_presented(self) -> bool:
        if isinstance(self.data, ModelContent):
            return self.data.flags.get(Flag.SKELETON, False) and self.options.skeleton
        return False

    @property
    def _animation_presented(self) -> bool:
        if isinstance(self.data, ModelContent):
            return self._skeleton_presented and self.options.animation
        return False
