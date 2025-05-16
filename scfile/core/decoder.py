"""
Base class for file decoder (parsing).
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional

from scfile import exceptions as exc
from scfile.core.base import BaseFile
from scfile.core.context.options import UserOptions
from scfile.core.encoder import FileEncoder
from scfile.core.io.streams import StructFileIO
from scfile.core.types import Content, PathLike
from scfile.enums import FileMode


class FileDecoder(BaseFile, StructFileIO, Generic[Content], ABC):
    mode: str = FileMode.READ

    _content: type[Content]

    def __init__(self, file: PathLike, options: Optional[UserOptions] = None):
        self.file = file
        self.options: UserOptions = options or UserOptions()
        self.data: Content = self._content()

        super().__init__(file=self.file, mode=self.mode)

    def prepare(self) -> None:
        pass

    @abstractmethod
    def parse(self) -> None:
        pass

    def decode(self) -> Content:
        self.prepare()
        self.validate()
        self.parse()
        self.seek(0)
        return self.data

    def convert_to(self, encoder: type[FileEncoder[Content]]) -> FileEncoder[Content]:
        data = self.decode()
        enc = encoder(data, self.options)
        enc.encode()
        return enc

    def convert(self, encoder: type[FileEncoder[Content]]) -> bytes:
        enc = self.convert_to(encoder)
        content = enc.getvalue()
        enc.close()
        return content

    def validate(self) -> None:
        if self.filesize <= len(self.signature or bytes()):
            raise exc.FileIsEmpty(self.path)

        if self.signature:
            read = self.read(len(self.signature))

            if read != self.signature:
                raise exc.FileSignatureInvalid(self.path, read, self.signature)

    def close(self) -> None:
        self.data.reset()
        super().close()
