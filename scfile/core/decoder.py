"""
Base class for file decoder (parsing).
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional

from scfile.core.base import BaseFile
from scfile.core.context.options import UserOptions
from scfile.core.encoder import FileEncoder
from scfile.core.io.streams import StructFileIO
from scfile.core.types import Content, PathLike
from scfile.enums import FileMode
from scfile.exceptions.file import EmptyFileError, InvalidSignatureError


class FileDecoder(BaseFile, StructFileIO, Generic[Content], ABC):
    """Base class for decoding file content into structured data objects."""

    mode: str = FileMode.READ

    _content: type[Content]

    def __init__(self, file: PathLike, options: Optional[UserOptions] = None):
        """Initialize file decoder with source file and options.

        Arguments:
            file: Path to file that will be decoded. Can be any `path-like` object.
            options (optional): User provided options. If None, default `UserOptions` will be used.

        Initialized:
            file (`PathLike`): The input file path.
            options (`UserOptions`): Decoding options (default or user provided).
            data (`Generic[Content]`): Empty instance of content type for storing decoded data.

        Note:
            Actual decoding doesn't happen during initialization.
            Call `decode()` to perform parsing process.
        """

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
            raise EmptyFileError(self.path)

        if self.signature:
            read = self.read(len(self.signature))

            if read != self.signature:
                raise InvalidSignatureError(self.path, read, self.signature)

    def close(self) -> None:
        self.data.reset()
        super().close()
