"""
Shared content data between decoder and encoder.
"""

from abc import ABC
from collections import defaultdict
from dataclasses import MISSING, dataclass, field, fields
from typing import Generic, TypeVar, cast

from scfile.structures.scene import ModelFlags, ModelScene
from scfile.structures.texture import CubemapTexture, DefaultTexture, Texture


TextureType = TypeVar("TextureType", bound=Texture)


@dataclass
class FileContent(ABC):
    """Base dataclass for file content storage."""

    def reset(self):
        for f in fields(self):
            if f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())

            elif f.default is not MISSING:
                setattr(self, f.name, f.default)

            else:
                setattr(self, f.name, None)


@dataclass
class ModelContent(FileContent):
    """Model content storage."""

    version: float = 0.0
    flags: ModelFlags = field(default_factory=lambda: defaultdict(bool))
    scene: ModelScene = field(default_factory=ModelScene)


@dataclass
class TextureContent(FileContent, Generic[TextureType]):
    """Texture content storage."""

    width: int = 0
    height: int = 0
    mipmap_count: int = 0
    format: bytes = field(default_factory=bytes)
    texture: TextureType = field(default_factory=lambda: cast(TextureType, DefaultTexture()))

    @property
    def is_cubemap(self) -> bool:
        return isinstance(self.texture, CubemapTexture)

    @property
    def is_compressed(self) -> bool:
        return self.fourcc in (b"DXT1", b"DXT3", b"DXT5", b"ATI2", b"DX10")

    @property
    def fourcc(self) -> bytes:
        match self.format:
            case b"DXN_XY":
                return b"ATI2"
            case b"RGBA32F":
                return b"DX10"
            case _:
                return self.format


@dataclass
class ImageContent(FileContent):
    """Image content storage."""

    image: bytes = field(default_factory=bytes)
