from io import BytesIO
from typing import Any

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

    def create(self) -> bytes:
        # it was pretty hard...
        self._write(
            Magic.PNG,
            self.filedata
        )

        return self.result

    def _write(self, *data: Any) -> None:
        for d in data:
            self._buffer.write(bytes(d))
