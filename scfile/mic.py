from scfile.base import BaseInputFile
from scfile.consts import Magic, Signature


class MicFile(BaseInputFile):
    @property
    def signature(self) -> int:
        return Signature.MIC

    def to_png(self) -> bytes:
        self._convert()
        return self.output

    def _convert(self) -> bytes:
        # since in all BaseFile's we read first 4 bytes
        # we simply write the new signature and rest of file data into buffer
        self.buffer.write(bytes(Magic.PNG))
        self.buffer.write(self.reader.read())

        return self.output
