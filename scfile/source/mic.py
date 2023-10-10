from scfile.consts import Signature
from scfile.output import PngFile

from .base import BaseSourceFile


class MicFile(BaseSourceFile):

    signature = Signature.MIC

    def to_png(self) -> bytes:
        return self.convert()

    def _default_output(self) -> None:
        PngFile(
            self.buffer,
            self.filename,
            self.filedata
        ).create()

    def _parse(self) -> None:
        self.filedata = self.reader.read()
