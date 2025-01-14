from abc import ABC, abstractmethod
from typing import Generic, Optional, Self, TypeVar

from scfile.enums import FileFormat, FileMode
from scfile.io.binary import StructBytesIO
from scfile.io.types import PathLike

from .context import FileContext
from .handler import FileHandler


Context = TypeVar("Context", bound=FileContext)
Opener = StructBytesIO


class FileEncoder(FileHandler[Context, Opener], Generic[Context], ABC):
    mode: FileMode = FileMode.WRITE
    signature: Optional[bytes] = None

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.buffer = self.b = Opener()

        super().__init__(self.ctx, self.buffer)

    @property
    @abstractmethod
    def format(self) -> FileFormat:
        pass

    def prepare(self) -> None:
        pass

    @abstractmethod
    def serialize(self) -> None:
        pass

    @property
    def suffix(self) -> str:
        return f".{self.format}"

    @property
    def content(self) -> bytes:
        return self.buffer.getvalue()

    def encode(self) -> Self:
        self.prepare()
        self.add_signature()
        self.serialize()
        return self

    def add_signature(self) -> None:
        if self.signature:
            self.buffer.write(self.signature)

    def save_as(self, path: PathLike) -> None:
        with open(path, mode=self.mode) as fp:
            fp.write(self.content)

    def save(self, path: PathLike) -> None:
        self.save_as(path=path)
        self.close()

    def export(self, filename: str) -> None:
        self.save(path=f"{filename}{self.suffix}")
