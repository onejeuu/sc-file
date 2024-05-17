from scfile.consts import Signature
from scfile.file.data import ImageData
from scfile.file.png import PngEncoder
from scfile.io import BinaryFileIO

from .._base import FileDecoder


class MicDecoder(FileDecoder[BinaryFileIO, ImageData]):
    def to_png(self):
        return self.convert_to(PngEncoder)

    @property
    def opener(self):
        return BinaryFileIO

    @property
    def signature(self):
        return Signature.MIC

    def create_data(self):
        return ImageData(self.image)

    def parse(self):
        self.image = self.f.read()
