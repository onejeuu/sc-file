from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scfile.core.data.base import FileData
from scfile.enums import FileFormat, FileMode
from scfile.io.binary import StructBytesIO
from scfile.io.types import PathLike

from .file import FileHandler
from .serializer import FileSerializer


Data = TypeVar("Data", bound=FileData)


class FileEncoder(FileHandler[StructBytesIO, Data], Generic[Data], ABC):
    mode: FileMode = FileMode.WRITE

    def __init__(self, data: Data):
        self.buffer = StructBytesIO()
        self.data = data

        self.serializer = self.file_serializer(self.buffer, self.data)

        super().__init__(self.buffer, self.data)

    @property
    @abstractmethod
    def format(self) -> FileFormat:
        pass

    @property
    def suffix(self) -> str:
        return f".{self.format}"

    @property
    @abstractmethod
    def file_serializer(self) -> type[FileSerializer]:
        pass

    def prepare(self):
        pass

    def encode(self):
        self.prepare()
        self.serializer.serialize()

    def content(self) -> bytes:
        return self.buffer.getvalue()

    # TODO: safer save methods
    # TODO: better working with suffix
    def save_as(self, path: PathLike):
        with open(path, mode=self.mode) as fp:
            fp.write(self.content())

    def save(self, path: PathLike):
        self.save_as(path=path)
        self.close()

    def export(self, filename: str):
        self.save(path=f"{filename}{self.suffix}")
