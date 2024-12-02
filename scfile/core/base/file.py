from abc import ABC
from typing import Generic, Optional, TypeVar

from scfile.core.data.base import FileData
from scfile.enums import ByteOrder, FileMode
from scfile.io.base import StructIO


Opener = TypeVar("Opener", bound=StructIO)
Data = TypeVar("Data", bound=FileData)


class FileHandler(Generic[Opener, Data], ABC):
    def __init__(self, buffer: Opener, data: Data):
        self.buffer = buffer
        self.data = data

    mode: FileMode

    order: ByteOrder = StructIO.order
    signature: Optional[bytes] = None

    def close(self):
        self.buffer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
