import pathlib
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from scfile.enums import FileMode
from scfile.io.file import StructFileIO
from scfile.io.types import PathLike

from .context import FileContext
from .encoder import FileEncoder
from .handler import FileHandler
from .options import FileOptions


Opener = TypeVar("Opener", bound=StructFileIO)
Context = TypeVar("Context", bound=FileContext)
Options = TypeVar("Options", bound=FileOptions)


class FileDecoder(FileHandler[Context, Opener], Generic[Context, Opener, Options], ABC):
    mode: FileMode = FileMode.READ

    def __init__(self, file: PathLike, options: Optional[Options] = None):
        self.file = file
        self.path = pathlib.Path(self.file)

        # Create base context and options
        self.ctx = self._context()
        self.options = options or self._options()

        # Create file reader
        self.buffer = self.f = self._opener(file=file, mode=self.mode)
        self.buffer.order = self.order

        super().__init__(self.ctx, self.buffer)

    # TODO: try rid out of duplications
    @property
    @abstractmethod
    def _opener(self) -> type[Opener]:
        pass

    @property
    @abstractmethod
    def _context(self) -> type[Context]:
        pass

    @property
    @abstractmethod
    def _options(self) -> type[Options]:
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
