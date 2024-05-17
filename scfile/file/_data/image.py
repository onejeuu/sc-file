from dataclasses import dataclass

from .base import FileData


@dataclass
class ImageData(FileData):
    image: bytes
