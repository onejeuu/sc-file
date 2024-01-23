from scfile.consts import Signature
from scfile.files.output.png import PngFile, PngOutputData

from .base import BaseSourceFile


class MicFile(BaseSourceFile):

    output = PngFile
    signature = Signature.MIC

    def to_png(self) -> bytes:
        return self.convert()

    @property
    def data(self) -> PngOutputData:
        return PngOutputData(self.imagedata)

    def parse(self) -> None:
        self.imagedata = self.r.read()
