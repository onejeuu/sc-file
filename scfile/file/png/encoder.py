from scfile.consts import Magic
from scfile.file._base import FileEncoder
from scfile.file._data import ImageData


class PngEncoder(FileEncoder[ImageData]):
    @property
    def magic(self):
        return Magic.PNG

    def serialize(self):
        self.b.write(self.data.image)
