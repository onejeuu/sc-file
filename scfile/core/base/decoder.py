import pathlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scfile.core.base.encoder import FileEncoder
from scfile.core.data.base import FileData
from scfile.enums import FileMode
from scfile.io.file import StructFileIO
from scfile.io.types import PathLike

from .file import FileHandler
from .parser import FileParser


Opener = TypeVar("Opener", bound=StructFileIO)
Data = TypeVar("Data", bound=FileData)
Parser = TypeVar("Parser", bound=FileParser)


class FileDecoder(FileHandler[Opener, Data], Generic[Opener, Data, Parser], ABC):
    mode: FileMode = FileMode.READ

    def __init__(self, file: PathLike):
        self.file = file
        self.path = pathlib.Path(self.file)
        self.filesize = self.path.stat().st_size

        self.buffer = self.f = self.opener(file=file, mode=self.mode)
        self.buffer.order = self.order

        self.data = self.file_data()

        self.parser = self.file_parser(self.buffer, self.data, self.path)

        super().__init__(self.buffer, self.data)

    @property
    @abstractmethod
    def opener(self) -> type[Opener]:
        pass

    @property
    @abstractmethod
    def file_data(self) -> type[Data]:
        pass

    @property
    @abstractmethod
    def file_parser(self) -> type[Parser]:
        pass

    def decode(self) -> Data:
        self.validate()
        self.parser.parse()

        return self.data

    # TODO: this kinda strange
    def convert_to(self, encoder: type[FileEncoder[Data]]) -> FileEncoder[Data]:
        data = self.decode()
        enc = encoder(data)
        enc.encode()
        return enc

    def convert(self, encoder: type[FileEncoder[Data]]) -> bytes:
        enc = self.convert_to(encoder)
        content = enc.content()
        enc.close()
        return content

    def validate(self) -> None:
        if self.signature:
            if readed := self.f.read(len(self.signature)) != self.signature:
                raise Exception(f"{readed} != {self.signature}")
