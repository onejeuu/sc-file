"""
Data structures for textures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import override

CUBEMAP_FACES = ("+x", "-x", "+y", "-y", "+z", "-z")
"""Cubemap face order."""

CUBEMAP_FACE_COUNT = len(CUBEMAP_FACES)
"""Number of faces in a cubemap."""


@dataclass
class Texture(ABC):
    """Base class for texture data."""

    @property
    @abstractmethod
    def image(self) -> bytes: ...

    @property
    @abstractmethod
    def linear_size(self) -> int: ...


@dataclass
class DefaultTexture(Texture):
    """Standard 2D texture with mipmaps."""

    uncompressed: list[int] = field(default_factory=list)
    compressed: list[int] = field(default_factory=list)
    mipmaps: list[bytes] = field(default_factory=list)

    @property
    @override
    def image(self) -> bytes:
        return b"".join(self.mipmaps)

    @property
    @override
    def linear_size(self) -> int:
        return self.uncompressed[0] if self.uncompressed else 0


@dataclass
class CubemapTexture(Texture):
    """Cubemap texture with face separated mipmaps."""

    uncompressed: list[list[int]] = field(default_factory=list)
    compressed: list[list[int]] = field(default_factory=list)
    faces: list[list[bytes]] = field(default_factory=lambda: [[] for _ in range(CUBEMAP_FACE_COUNT)])

    @property
    @override
    def image(self) -> bytes:
        return b"".join(b"".join(face) for face in self.faces)

    @property
    @override
    def linear_size(self) -> int:
        return self.uncompressed[0][0] if self.uncompressed and self.uncompressed[0] else 0
