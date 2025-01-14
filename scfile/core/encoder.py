from abc import ABC, abstractmethod
from typing import Generic, Optional, Self

from scfile.enums import FileFormat, FileMode
from scfile.io.streams import StructBytesIO
from scfile.io.types import PathLike

from .handler import FileHandler
from .types import Context, Options


Opener = StructBytesIO


class FileEncoder(FileHandler[Opener, Context], Generic[Context, Options], ABC):
    mode: FileMode = FileMode.WRITE

    format: FileFormat
    signature: Optional[bytes] = None

    _options: type[Options]

    def __init__(self, ctx: Context, options: Optional[Options] = None):
        self.ctx: Context = ctx

        self.buffer: Opener = Opener()
        self.options: Options = options or self._options()

        # Buffer abbreviation
        self.b = self.buffer

        super().__init__(self.buffer, self.ctx)

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
