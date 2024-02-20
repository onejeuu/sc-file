from abc import ABC, abstractmethod
from io import IOBase


class BaseFile(ABC):
    @property
    @abstractmethod
    def buffer(self) -> IOBase:
        pass

    def close(self):
        self.buffer.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
