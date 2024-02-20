from abc import ABC
from dataclasses import dataclass

from scfile.utils.model import Model


class FileData(ABC):
    pass

@dataclass
class ModelData(FileData):
    model: Model
    texture: bool
    normals: bool

@dataclass
class TextureData(FileData):
    width: int
    height: int
    linear_size: int
    fourcc: bytes
    image: bytes

@dataclass
class ImageData(FileData):
    image: bytes
