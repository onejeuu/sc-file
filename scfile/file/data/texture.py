from dataclasses import dataclass

from .base import FileData


@dataclass
class TextureData(FileData):
    width: int
    height: int
    linear_size: int
    fourcc: bytes
    image: bytes
