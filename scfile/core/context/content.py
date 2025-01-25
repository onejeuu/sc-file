import dataclasses
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field, fields

from scfile.geometry.scene import ModelFlags, ModelScene


@dataclass
class FileContent(ABC):
    def reset(self):
        for f in fields(self):
            if f.default_factory is not dataclasses.MISSING:
                setattr(self, f.name, f.default_factory())

            elif f.default is not dataclasses.MISSING:
                setattr(self, f.name, f.default)

            else:
                setattr(self, f.name, None)


@dataclass
class ModelContent(FileContent):
    version: float = 0.0
    flags: ModelFlags = field(default_factory=lambda: defaultdict(bool))
    scene: ModelScene = field(default_factory=ModelScene)

    @property
    def meshes(self):
        return self.scene.meshes

    @property
    def skeleton(self):
        return self.scene.skeleton


@dataclass
class TextureContent(FileContent):
    width: int = 0
    height: int = 0
    mipmap_count: int = 0
    fourcc: bytes = field(default_factory=bytes)
    uncompressed: list[int] = field(default_factory=list)
    compressed: list[int] = field(default_factory=list)
    mipmaps: list[bytes] = field(default_factory=list)
    is_hdri: bool = False

    @property
    def image(self):
        return b"".join(self.mipmaps)

    @property
    def linear_size(self):
        return self.uncompressed[0]


@dataclass
class ImageContent(FileContent):
    image: bytes = field(default_factory=bytes)
