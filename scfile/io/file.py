import io

from scfile.io.base import StructIO


class StructFileIO(io.FileIO, StructIO):
    pass
