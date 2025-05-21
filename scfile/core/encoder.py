"""
Base class for file encoder (serialization).
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Self

from scfile.core.base import BaseFile
from scfile.core.context.options import UserOptions
from scfile.core.io.streams import StructBytesIO
from scfile.core.types import Content, PathLike
from scfile.enums import FileMode


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
            ctx (`dict[str, Any]`): Empty context dictionary for processing state.

        Note:
            Actual encoding doesn't happen during initialization.
            Call `encode()` to perform serialization process.
        """

        self.data: Content = data
        self.options: UserOptions = options or UserOptions()
        self.ctx: dict[str, Any] = {}

    def prepare(self) -> None:
        pass

    @abstractmethod
    def serialize(self) -> None:
        pass

    @property
    def suffix(self) -> str:
        return f".{self.format}"

    def encode(self) -> Self:
        self.prepare()
        self.add_signature()
        self.serialize()
        return self

    def add_signature(self) -> None:
        if self.signature:
            self.write(self.signature)

    def save_as(self, path: PathLike) -> None:
        with open(path, mode=self.mode) as fp:
            fp.write(self.getvalue())

    def save(self, path: PathLike) -> None:
        self.save_as(path=path)
        self.close()

    def export(self, filename: str) -> None:
        self.save(path=f"{filename}{self.suffix}")

    def close(self) -> None:
        self.data.reset()
        self.ctx = {}
        super().close()
