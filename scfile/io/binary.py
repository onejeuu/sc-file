import io
import pathlib

from scfile.exceptions import FileStructureInvalid

from .base import BinaryIO


class BinaryBytesIO(io.BytesIO, BinaryIO):
    pass


class BinaryFileIO(io.FileIO, BinaryIO):  # type: ignore
    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(str(self.name))

    def validate_buffer_size(self, size: int):
        current_pos = self.tell()
        self.seek(0, io.SEEK_END)
        file_size = self.tell()

        # return pointer
        self.seek(current_pos)

        remaining = file_size - current_pos

        if remaining < size:
            raise FileStructureInvalid(self.path, current_pos)
