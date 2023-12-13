from dataclasses import dataclass

from scfile.consts import Magic

from .base import BaseOutputFile, OutputData


@dataclass
class PngOutputData(OutputData):
    image: bytes


class PngFile(BaseOutputFile[PngOutputData]):

    magic = Magic.PNG

    def write(self) -> None:
        self._raw_write(self.data.image)
