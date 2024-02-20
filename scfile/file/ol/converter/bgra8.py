from .base import RGBA8Converter


class BGRA8Converter(RGBA8Converter):
    def to_rgba8(self) -> bytes:
        rgba = self.array[:, :, [2, 1, 0, 3]]
        return rgba.tobytes()
