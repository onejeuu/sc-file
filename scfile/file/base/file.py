from abc import ABC, abstractmethod
from io import IOBase
from typing import Any, Optional, Type

from scfile.file.data import FileData


class BaseFile(ABC):
    @property
    @abstractmethod
    def buffer(self) -> IOBase:
        """IOBase buffer for reading or writing data."""
        pass

    @property
    @abstractmethod
    def data(self) -> Optional[FileData]:
        """Parsed file data."""
        pass

    def close(self):
        """Closes buffer handler."""
        self.buffer.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        self.close()
