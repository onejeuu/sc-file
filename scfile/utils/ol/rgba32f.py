import numpy as np

from .converter import RGBA8Converter


class RGBA32FConverter(RGBA8Converter):
    dtype = np.float32

    def to_rgba8(self) -> bytes:
        rgba = (self.array * 255).astype(np.uint8)
        return rgba.tobytes()
