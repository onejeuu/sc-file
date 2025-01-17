import io
from pathlib import Path

from scfile import exceptions as exc
from scfile.io.base import StructIO


class StructBytesIO(io.BytesIO, StructIO):
    pass


class StructFileIO(io.FileIO, StructIO):
    @property
    def path(self) -> Path:
        return Path(str(self.name))

    def _validate_buffer(self, size: int):
        current_pos = self.tell()
        self.seek(0, io.SEEK_END)
        file_size = self.tell()

        # return pointer
        self.seek(current_pos)
        remaining = file_size - current_pos

        if remaining < size:
            raise exc.FileStructureInvalid(self.path, current_pos)
