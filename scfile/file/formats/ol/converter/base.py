import numpy as np


class RGBA8Converter:
    channels = 4
    dtype = np.uint8

    def __init__(self, image: bytes, width: int, height: int):
        self.image = image
        self.width = width
        self.height = height
        self.array = self.generate_image_array()

    def generate_image_array(self):
        array = np.frombuffer(self.image, dtype=self.dtype)
        array = array.reshape((self.height, self.width, self.channels))
        return array

    def invert(self) -> bytes:
        inverted = 255 - self.array[:, :, :3]
        inverted = np.concatenate((inverted, self.array[:, :, 3:]), axis=2)
        return inverted.astype(np.uint8).tobytes()
