"""Content representation containers."""

from dataclasses import dataclass, field
from typing import ClassVar

from scfile.enums import FileKind

from .models import Feature, ModelMeta, ModelScene
from .regions import RegionChunk
from .textures import CubemapTexture, DefaultTexture, Texture, TextureMeta


type DocumentPrimitive = int | float | bytes | str
type DocumentValue = None | DocumentPrimitive | list[DocumentValue] | dict[str, DocumentValue]

type ArchiveEntry = tuple[str, bytes]


class BaseContent:
    """Base class for content representations."""

    kind: ClassVar[FileKind]


@dataclass
class ModelContent(BaseContent):
    """Content representation of 3D model."""

    kind: ClassVar[FileKind] = FileKind.MODEL

    meta: ModelMeta = field(default_factory=ModelMeta)
    scene: ModelScene = field(default_factory=ModelScene)

    def has(
        self,
        feature: Feature,
    ) -> bool:
        return self.scene.has(feature)


@dataclass
class TextureContent(BaseContent):
    """Content representation of texture."""

    kind: ClassVar[FileKind] = FileKind.TEXTURE

    width: int = 0
    height: int = 0
    meta: TextureMeta = field(default_factory=TextureMeta)
    texture: Texture = field(default_factory=DefaultTexture)

    @property
    def is_cubemap(self) -> bool:
        return isinstance(self.texture, CubemapTexture)

    @property
    def is_compressed(self) -> bool:
        return self.fourcc in (b"DXT1", b"DXT3", b"DXT5", b"ATI1", b"ATI2", b"DX10")

    @property
    def fourcc(self) -> bytes:
        match self.meta.format:
            case b"DXN_X":
                return b"ATI1"
            case b"DXN_XY":
                return b"ATI2"
            case b"RGBA32F":
                return b"DX10"
            case _:
                return self.meta.format


@dataclass
class ImageContent(BaseContent):
    """Content representation of image."""

    kind: ClassVar[FileKind] = FileKind.IMAGE

    image: bytes = field(default_factory=bytes)


@dataclass
class ArchiveContent(BaseContent):
    """Content representation of archive."""

    kind: ClassVar[FileKind] = FileKind.ARCHIVE

    entries: list[ArchiveEntry] = field(default_factory=list)


@dataclass
class DocumentContent(BaseContent):
    """Content representation of structured document."""

    kind: ClassVar[FileKind] = FileKind.DOCUMENT

    value: DocumentValue = None


@dataclass
class RegionContent(BaseContent):
    """Content representation of world region."""

    kind: ClassVar[FileKind] = FileKind.REGION

    rx: int = 0
    rz: int = 0

    sector_offsets: list[int] = field(default_factory=list)
    sector_counts: list[int] = field(default_factory=list)
    uuids: list[bytes] = field(default_factory=list)

    chunks: list[RegionChunk] = field(default_factory=list)
