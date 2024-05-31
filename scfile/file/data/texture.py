from dataclasses import dataclass

from .base import FileData


@dataclass
class TextureData(FileData):
    width: int
    height: int
    mipmap_count: int
    linear_size: int
    fourcc: bytes
    image: bytes
