from scfile.consts import Signature
from scfile.output import PngFile

from .base import BaseSourceFile


class MicFile(BaseSourceFile):
    @property
    def signature(self) -> int:
        return Signature.MIC

    def to_png(self) -> bytes:
        return self.convert()

    def convert(self) -> bytes:
        # writing converted to png file bytes into buffer
        PngFile(
            self.buffer,
            self.filename,
            self.reader.read()
        ).create()

        return self.result

    def _parse(self) -> None:
        pass
