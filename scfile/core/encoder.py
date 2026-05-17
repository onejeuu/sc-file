"""
Base class for file encoder (serialization).
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Self, TypeAlias

from scfile.enums import FileMode
from scfile.structures.models import Flag
from scfile.structures.models.transforms import SceneTransform
from scfile.types import PathLike

from .base import BaseFile
from .context import ContentType, ModelContent, UserOptions
from .io import StructBytesIO


EncoderContext: TypeAlias = dict[str, Any]


class FileEncoder(BaseFile, StructBytesIO, Generic[ContentType], ABC):
    """Base class for encoding structured data objects into file content."""

    transforms: Optional[list[SceneTransform]] = None

    @property
    def mode(self) -> str:
        return FileMode.WRITE

    def __init__(self, data: ContentType, options: Optional[UserOptions] = None):
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

    @property
    def suffix(self) -> str:
        """Return standard file extension for this format (with dot)."""
        return self.format.suffix

    def encode(self) -> Self:
        """Encode data: prelude, apply transform, add signature, serialize. Returns self."""
        self.prelude()
        self.transform()
        self.add_signature()
        self.serialize()
        return self

    def prelude(self) -> None:
        """Runs before file transform and serialization."""
        pass

    def transform(self):
        if self.transforms and isinstance(self.data, ModelContent):
            scene = self.data.scene
            for transform in self.transforms:
                scene = transform(scene)
            self.data.scene = scene

    def add_signature(self) -> None:
        """Write format signature (magic bytes) to buffer if defined."""
        if self.signature:
            self.write(self.signature)

    @abstractmethod
    def serialize(self) -> None:
        """Convert structured `self.data` into bytes and write to buffer."""
        pass

    def save_as(self, path: PathLike) -> None:
        """Write buffer content to file. Keeps encoder open."""
        with open(path, mode=self.mode) as fp:
            fp.write(self.getvalue())

    def export_as(self, path: PathLike) -> None:
        """Save to path (without suffix) adding format suffix automatically. Keeps encoder open."""
        self.save_as(path=f"{path}{self.suffix}")

    def save(self, path: PathLike) -> None:
        """Write buffer content to file. Closes encoder."""
        self.save_as(path=path)
        self.close()

    def export(self, path: PathLike) -> None:
        """Save to path (without suffix) adding format suffix automatically. Closes encoder."""
        self.save(path=f"{path}{self.suffix}")
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
