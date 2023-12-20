from abc import ABC

from scfile.files.output.dds import DdsOutputData


class Converter(ABC):
    def __init__(self, data: DdsOutputData):
        self.data = data
