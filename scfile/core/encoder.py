"""
Base class for file encoder (serialization).
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Self

from scfile.core.base import BaseFile
from scfile.core.io.streams import StructBytesIO
from scfile.core.types import Content, Options, PathLike
from scfile.enums import FileMode


class FileEncoder(BaseFile, StructBytesIO, Generic[Content, Options], ABC):
    @property
    def mode(self) -> str:
        return FileMode.WRITE

    _options: type[Options]

    def __init__(self, data: Content, options: Optional[Options] = None):
        self.data: Content = data
        self.options: Options = options or self._options()
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
