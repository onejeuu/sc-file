from .base import BaseSourceFile
from .consts import Magic, Signature


class MicFile(BaseSourceFile):
    @property
    def signature(self) -> int:
        return Signature.MIC

    def to_png(self) -> bytes:
        return self.convert()

    def convert(self) -> bytes:
        self._parse()
        return self.output

    def _parse(self) -> bytes:
        # since in all BaseFile's we read first 4 bytes
        # we simply write the new signature and rest of file data into buffer
        self.buffer.write(bytes(Magic.PNG))
        self.buffer.write(self.reader.read())

        return self.output
