from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scfile.core.data.base import FileData
from scfile.io.binary import StructBytesIO


Data = TypeVar("Data", bound=FileData)


class FileSerializer(Generic[Data], ABC):
    def __init__(self, buffer: StructBytesIO, data: Data):
        self.buffer = self.b = buffer
        self.data = data

    @abstractmethod
    def serialize(self):
        pass
