from scfile.consts import Signature
from scfile.files import PngFile

from .base import BaseSourceFile


class MicFile(BaseSourceFile):

    signature = Signature.MIC

    def to_png(self) -> bytes:
        return self.convert()

    def _output(self) -> PngFile:
        return PngFile(
            self.buffer,
            self.filename,
            self.filedata
        )

    def _parse(self) -> None:
        self.filedata = self.reader.read()
