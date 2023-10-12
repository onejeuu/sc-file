from abc import ABC, abstractmethod
from io import BytesIO


class BaseOutputFile(ABC):
    DEFAULT_FILENAME = "file"

    def __init__(
        self,
        buffer: BytesIO,
        filename: str = DEFAULT_FILENAME
    ):
        self.buffer = buffer
        self.filename = filename

    def create(self) -> bytes:
        """Create output file. Return output file bytes."""
        self._create()
        return self.result

    @abstractmethod
    def _create(self) -> None:
        """Create output file in buffer."""
        ...

    @property
    def result(self) -> bytes:
        """Result bytes of conversion."""
        return self.buffer.getvalue()

    def __str__(self):
        return f"<{self.__class__.__name__}> filename='{self.filename}'"
