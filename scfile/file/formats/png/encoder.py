from scfile.consts import Magic
from scfile.enums import FileSuffix
from scfile.file.base import FileEncoder
from scfile.file.data import ImageData


class PngEncoder(FileEncoder[ImageData]):
    @property
    def magic(self):
        return Magic.PNG

    @classmethod
    def suffix(cls):
        return FileSuffix.PNG

    def serialize(self):
        self.b.write(self.data.image)
