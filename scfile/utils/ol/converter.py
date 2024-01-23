from abc import ABC, abstractmethod

import numpy as np

from scfile.files.output.dds import DdsOutputData


class RGBA8Converter(ABC):
    channels = 4
    dtype = np.uint8

    def __init__(self, data: DdsOutputData):
        self.data = data

    @property
    def array(self):
        array = np.frombuffer(self.data.image, dtype=self.dtype)
        array = array.reshape((self.data.height, self.data.width, self.channels))
        return array

    @abstractmethod
    def to_rgba8(self) -> bytes:
        pass
