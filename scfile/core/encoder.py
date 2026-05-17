from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Generic, Optional, Self, TypeAlias

from scfile.structures.models import Flag
from scfile.structures.models.transforms import SceneTransform
from scfile.types import PathLike

from .base import BaseFile, IOStream
from .content import ContentType, ModelContent
from .options import UserOptions


EncoderContext: TypeAlias = dict[str, Any]
EncoderTransforms: TypeAlias = Optional[list[SceneTransform]]


class FileEncoder(BaseFile, Generic[ContentType], ABC):
    """Base class for encoding structured data objects into file content."""

    transforms: EncoderTransforms = None

    def __init__(
        self,
        data: ContentType,
        options: Optional[UserOptions] = None,
        output: Optional[IOStream] = None,
    ):
        """Initialize file encoder with content data and options.

        Arguments:
            data: Content data to be encoded.
            options (optional): User provided options. If None, default `UserOptions` will be used.

        Initialized:
            data (`Generic[Content]`): Content to encode.
            options (`UserOptions`): Encoding options (default or user provided).
            ctx (`EncoderContext`): Empty context dictionary for processing state.

        Note:
            Actual encoding doesn't happen during initialization.
            Call `encode()` to perform serialization process.
        """

        self.data: ContentType = data
        self.options: UserOptions = options or UserOptions()
        self.ctx: EncoderContext = {}

        super().__init__(output or BytesIO(), mode="wb")

    @property
    def suffix(self) -> str:
        """Return standard file extension for this format (with dot)."""
        return self.format.suffix

    def encode(
        self,
        transforms: EncoderTransforms = None,
    ) -> Self:
        """Encode data: prelude, apply transform, add signature, serialize. Returns self."""
        self.prelude()
        self.transform(transforms=transforms)
        self.add_signature()
        self.serialize()
        return self

    def prelude(self) -> None:
        """Runs before file transform and serialization."""
        pass

    def transform(
        self,
        transforms: EncoderTransforms = None,
    ):
        transforms = transforms or self.transforms
        if transforms and isinstance(self.data, ModelContent):
            scene = self.data.scene
            for tr in transforms:
                scene = tr(scene)
            self.data.scene = scene

    def add_signature(self) -> None:
        """Write format signature (magic bytes) to buffer if defined."""
        if self.signature:
            self.write(self.signature)

    @abstractmethod
    def serialize(self) -> None:
        """Convert structured `self.data` into bytes and write to buffer."""
        pass

    def save_as(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """Write buffer content to file. Keeps encoder open."""
        with open(path, mode=mode) as fp:
            fp.write(self.getvalue())

    def export_as(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """Save to path (without suffix) adding format suffix automatically. Keeps encoder open."""
        self.save_as(path=f"{path}{self.suffix}", mode=mode)

    def save(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """Write buffer content to file. Closes encoder."""
        self.save_as(path=path, mode=mode)
        self.close()

    def export(
        self,
        path: PathLike,
        mode: str = "wb",
    ) -> None:
        """Save to path (without suffix) adding format suffix automatically. Closes encoder."""
        self.save(path=f"{path}{self.suffix}", mode=mode)
        self.close()

    def close(self) -> None:
        """Close buffer and reset `self.ctx` state. Same as `BytesIO.close()`."""
        self.ctx = {}
        super().close()

    @property
    def _skeleton_presented(self) -> bool:
        if isinstance(self.data, ModelContent):
            return self.data.flags.get(Flag.SKELETON, False) and self.options.parse_skeleton
        return False

    @property
    def _animation_presented(self) -> bool:
        if isinstance(self.data, ModelContent):
            return self._skeleton_presented and self.options.parse_animation
        return False
