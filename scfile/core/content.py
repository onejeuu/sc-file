"""
Shared content data containers for handlers.
Defines data structures that hold parsed file contents.
"""

from abc import ABC
from collections import defaultdict
from dataclasses import MISSING, dataclass, field, fields
from typing import Generic, TypeAlias, TypeVar, cast
from uuid import UUID

from scfile.enums import FileType
from scfile.structures.models import ModelFlags, ModelScene
from scfile.structures.regions import RegionChunk
from scfile.structures.textures import CubemapTexture, DefaultTexture, TextureType


NbtValue: TypeAlias = None | int | float | bytes | str | list[int] | list["NbtValue"] | dict[str, "NbtValue"]


@dataclass
class BaseContent(ABC):
    """Base class for file content types."""

    type: FileType = field(default=FileType.NONE)

    def reset(self):
        for f in fields(self):
            if f.default_factory is not MISSING:
                setattr(self, f.name, f.default_factory())

            elif f.default is not MISSING:
                setattr(self, f.name, f.default)


ContentType = TypeVar("ContentType", bound=BaseContent)


@dataclass
class ModelContent(BaseContent):
    """Content container for 3D models."""

    type: FileType = field(default=FileType.MODEL)

    version: float = 0.0
    flags: ModelFlags = field(default_factory=lambda: defaultdict(bool))
    scene: ModelScene = field(default_factory=ModelScene)


@dataclass
class TextureContent(BaseContent, Generic[TextureType]):
    """Content container for textures (2D or cubemap)."""

    type: FileType = field(default=FileType.TEXTURE)

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
class ImageContent(BaseContent):
    """Content container for images."""

    type: FileType = field(default=FileType.IMAGE)

    image: bytes = field(default_factory=bytes)


@dataclass
class TexarrContent(BaseContent):
    """Content container for texture arrays."""

    type: FileType = field(default=FileType.TEXARR)

    count: int = 0
    textures: list[tuple[str, bytes]] = field(default_factory=list)


@dataclass
class NbtContent(BaseContent):
    """Content container for NBT (Named Binary Tag) data."""

    type: FileType = field(default=FileType.NBT)

    value: NbtValue = None


@dataclass
class RegionContent(BaseContent):
    """Content container for regions (world terrain)."""

    type: FileType = field(default=FileType.REGION)

    rx: int = 0
    rz: int = 0

    offsets: list[int] = field(default_factory=list)
    counts: list[int] = field(default_factory=list)
    uuid: list[UUID] = field(default_factory=list)

    chunks: list[RegionChunk] = field(default_factory=list)
