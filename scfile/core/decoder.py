import pathlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scfile.enums import FileMode
from scfile.io.file import StructFileIO
from scfile.io.types import PathLike

from .context import FileContext
from .encoder import FileEncoder
from .handler import FileHandler


Opener = TypeVar("Opener", bound=StructFileIO)
Context = TypeVar("Context", bound=FileContext)


class FileDecoder(FileHandler[Opener, Context], Generic[Opener, Context], ABC):
    mode: FileMode = FileMode.READ

    def __init__(self, file: PathLike):
        self.file = file
        self.path = pathlib.Path(self.file)

        self.buffer = self.f = self.type_opener(file=file, mode=self.mode)
        self.buffer.order = self.order

        self.ctx = self.type_context()

        super().__init__(self.buffer, self.ctx)

    @property
    @abstractmethod
    def type_opener(self) -> type[Opener]:
        pass

    @property
    @abstractmethod
    def type_context(self) -> type[Context]:
        pass

    @abstractmethod
    def parse(self) -> None:
        pass

    def decode(self) -> Context:
        self.validate()
        self.parse()
        return self.ctx

    def convert_to(self, encoder: type[FileEncoder[Context]]) -> FileEncoder[Context]:
        data = self.decode()
        enc = encoder(data)
        enc.encode()
        return enc

    def convert(self, encoder: type[FileEncoder[Context]]) -> bytes:
        enc = self.convert_to(encoder)
        content = enc.content
        enc.close()
        return content

    def validate(self) -> None:
        if self.signature:
            if readed := self.f.read(len(self.signature)) != self.signature:
                raise Exception(f"{readed} != {self.signature}")
