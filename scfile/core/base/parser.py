from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from scfile.core.data.base import FileData
from scfile.io.file import StructFileIO


Opener = TypeVar("Opener", bound=StructFileIO)
Data = TypeVar("Data", bound=FileData)


class FileParser(Generic[Opener, Data], ABC):
    def __init__(self, buffer: Opener, data: Data, path: Path):
        self.buffer = self.f = buffer
        self.data = data
        self.path = path

    @abstractmethod
    def parse(self):
        pass
