from io import BytesIO

from scfile.consts import Magic

from .base import BaseOutputFile


class PngFile(BaseOutputFile):
    def __init__(
        self,
        buffer: BytesIO,
        filename: str,
        filedata: bytes
    ):
        super().__init__(buffer, filename)
        self.filedata = filedata

    def _create(self) -> None:
        # it was pretty hard...
        self.buffer.write(bytes(Magic.PNG))
        self.buffer.write(self.filedata)
