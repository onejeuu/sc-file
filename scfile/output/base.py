from abc import ABC, abstractmethod
from io import BytesIO


class BaseOutputFile(ABC):
    DEFAULT_FILENAME = "file"

    def __init__(
        self,
        buffer: BytesIO,
        filename: str = DEFAULT_FILENAME
    ):
        self._buffer = buffer
        self.filename = filename

    @abstractmethod
    def create(self) -> bytes:
        """Writes in buffer output file bytes."""
        ...

    @property
    def result(self) -> bytes:
        """Returns buffer bytes."""
        return self._buffer.getvalue()

    def __str__(self):
        return f"<{self.__class__.__name__}> filename='{self.filename}'"
