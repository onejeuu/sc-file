"""
Shared content data containers for handlers.
Defines data structures that hold parsed file contents.
"""

from dataclasses import dataclass, field
from typing import ClassVar, cast
from uuid import UUID

from scfile.enums import FileType
from scfile.structures.models import Feature, FeatureFlags, ModelScene
from scfile.structures.regions import RegionChunk
from scfile.structures.textures import CubemapTexture, DefaultTexture, Texture


type DocumentPrimitive = int | float | bytes | str
type DocumentValue = None | DocumentPrimitive | list[DocumentValue] | dict[str, DocumentValue]


class BaseContent:
    """Base type for structured handler content."""

    type: ClassVar[FileType]


@dataclass
class ModelContent(BaseContent):
    """Content container for 3D models."""

    type: ClassVar[FileType] = FileType.MODEL

    version: float = 0.0
    flags: FeatureFlags = field(default_factory=dict)
    scene: ModelScene = field(default_factory=ModelScene)

    def has(
        self,
        feature: Feature,
    ) -> bool:
        return self.scene.has(feature)


@dataclass
class TextureContent[TextureType: Texture = DefaultTexture](BaseContent):
    """Content container for textures (2D or cubemap)."""

    type: ClassVar[FileType] = FileType.TEXTURE

    width: int = 0
    height: int = 0
    mipmap_count: int = 0
    format: bytes = field(default_factory=bytes)
    texture: TextureType = field(default_factory=lambda: cast(TextureType, DefaultTexture()))
    path_hash: bytes = field(default_factory=bytes)

    @property
    def is_cubemap(self) -> bool:
        return isinstance(self.texture, CubemapTexture)

    @property
    def is_compressed(self) -> bool:
        return self.fourcc in (b"DXT1", b"DXT3", b"DXT5", b"ATI1", b"ATI2", b"DX10")

    @property
    def fourcc(self) -> bytes:
        match self.format:
            case b"DXN_X":
                return b"ATI1"
            case b"DXN_XY":
                return b"ATI2"
            case b"RGBA32F":
                return b"DX10"
            case _:
                return self.format


@dataclass
class ImageContent(BaseContent):
    """Content container for images."""

    type: ClassVar[FileType] = FileType.IMAGE

    image: bytes = field(default_factory=bytes)


@dataclass
class TexarrContent(BaseContent):
    """Content container for texture arrays."""

    type: ClassVar[FileType] = FileType.TEXARR

    count: int = 0
    textures: list[tuple[str, bytes]] = field(default_factory=list)


@dataclass
class DocumentContent(BaseContent):
    """Content container for structured document data."""

    type: ClassVar[FileType] = FileType.DOCUMENT

    value: DocumentValue = None


@dataclass
class RegionContent(BaseContent):
    """Content container for regions (world terrain)."""

    type: ClassVar[FileType] = FileType.REGION

    rx: int = 0
    rz: int = 0

    offsets: list[int] = field(default_factory=list)
    counts: list[int] = field(default_factory=list)
    uuid: list[UUID] = field(default_factory=list)

    chunks: list[RegionChunk] = field(default_factory=list)
