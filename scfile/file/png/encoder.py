from scfile.consts import Magic
from scfile.file.data import ImageData
from scfile.file.encoder import FileEncoder


class PngEncoder(FileEncoder[ImageData]):
    @property
    def magic(self):
        return Magic.PNG

    def serialize(self):
        self.b.write(self.data.image)
