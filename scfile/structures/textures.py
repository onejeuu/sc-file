"""
Dataclasses for game specific textures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from scfile.consts import CubemapFaces


@dataclass
class Texture(ABC):
    """Base dataclass representing texture."""

    @property
    @abstractmethod
    def image(self) -> bytes:
        pass

    @property
    @abstractmethod
    def linear_size(self) -> int:
        pass


TextureType = TypeVar("TextureType", bound=Texture)


@dataclass
class DefaultTexture(Texture):
    """Standard 2D texture with mipmaps."""

    uncompressed: list[int] = field(default_factory=list)
    compressed: list[int] = field(default_factory=list)
    mipmaps: list[bytes] = field(default_factory=list)

    @property
    def image(self):
        return b"".join(self.mipmaps)

    @property
    def linear_size(self):
        return self.uncompressed[0]


@dataclass
class CubemapTexture(Texture):
    """Cube map texture with face separated mipmaps."""

    uncompressed: list[list[int]] = field(default_factory=list)
    compressed: list[list[int]] = field(default_factory=list)
    faces: list[list[bytes]] = field(default_factory=lambda: [[] for _ in range(CubemapFaces.COUNT)])

    @property
    def image(self):
        return b"".join(b"".join(face) for face in self.faces)

    @property
    def linear_size(self):
        return self.uncompressed[0][0]
