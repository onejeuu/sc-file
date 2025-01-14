import io

from scfile.io.base import StructIO


class StructBytesIO(io.BytesIO, StructIO):
    pass


class StructFileIO(io.FileIO, StructIO):
    pass
