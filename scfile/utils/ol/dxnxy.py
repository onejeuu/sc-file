import numpy as np

from .converter import RGBA8Converter


class DXNXYConverter(RGBA8Converter):
    # TODO: you know.
    def to_rgba8(self) -> bytes:
        ...
