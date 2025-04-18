from abc import ABC, abstractmethod
from typing import Generic, Optional

from scfile import exceptions as exc
from scfile.core.base import BaseFile
from scfile.core.encoder import FileEncoder
from scfile.core.io.streams import StructFileIO
from scfile.core.types import Content, Options, PathLike
from scfile.enums import FileMode


class FileDecoder(BaseFile, StructFileIO, Generic[Content, Options], ABC):
    mode: str = FileMode.READ

    _content: type[Content]
    _options: type[Options]

    def __init__(self, file: PathLike, options: Optional[Options] = None):
        self.file = file
        self.options: Options = options or self._options()
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

    def convert_to(self, encoder: type[FileEncoder[Content, Options]]) -> FileEncoder[Content, Options]:
        data = self.decode()
        enc = encoder(data, self.options)
        enc.encode()
        return enc

    def convert(self, encoder: type[FileEncoder[Content, Options]]) -> bytes:
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
