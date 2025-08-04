"""
Base class for file encoder (serialization).
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Self, TypeAlias

from scfile.enums import FileMode
from scfile.structures.flags import Flag
from scfile.types import PathLike

from .base import BaseFile
from .context import ModelContent, UserOptions
from .io import StructBytesIO
from .types import Content


EncoderContext: TypeAlias = dict[str, Any]


class FileEncoder(BaseFile, StructBytesIO, Generic[Content], ABC):
    """Base class for encoding structured data objects into file content."""

    @property
    def mode(self) -> str:
        return FileMode.WRITE

    def __init__(self, data: Content, options: Optional[UserOptions] = None):
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

        self.data: Content = data
        self.options: UserOptions = options or UserOptions()
        self.ctx: EncoderContext = {}

    @property
    def suffix(self) -> str:
        """Return standard file extension for this format (with dot)."""
        return self.format.suffix

    def encode(self) -> Self:
        """Encode data: prepare, add signature, serialize. Returns self."""
        self.prepare()
        self.add_signature()
        self.serialize()
        return self

    def encoded(self) -> Self:
        """Context manager that automatically encodes data on exit."""
        return self.encode()

    def prepare(self) -> None:
        """Perform preparations before serialization. *(e.g. calculations in content)*."""
        pass

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
            return self.data.flags[Flag.SKELETON] and self.options.parse_skeleton
        return False

    @property
    def _animation_presented(self) -> bool:
        return self._skeleton_presented and self.options.parse_animation
