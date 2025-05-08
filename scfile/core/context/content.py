"""
Shared content data between decoder and encoder.
"""

from abc import ABC
from collections import defaultdict
from dataclasses import MISSING, dataclass, field, fields
from typing import Generic, TypeVar, cast

from scfile.structures.animation import ModelAnimation
from scfile.structures.scene import ModelFlags, ModelScene
from scfile.structures.texture import DefaultTexture, Texture


TextureType = TypeVar("TextureType", bound=Texture)


@dataclass
class FileContent(ABC):
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
    version: float = 0.0
    flags: ModelFlags = field(default_factory=lambda: defaultdict(bool))
    scene: ModelScene = field(default_factory=ModelScene)

    @property
    def meshes(self):
        return self.scene.meshes

    @property
    def skeleton(self):
        return self.scene.skeleton

    @property
    def animation(self):
        return self.scene.animation


@dataclass
class AnimationContent(FileContent):
    version: float = 0.0
    bones_count: int = 0
    unknown: int = 0
    clips_count: int = 0
    animation: ModelAnimation = field(default_factory=ModelAnimation)


@dataclass
class TextureContent(FileContent, Generic[TextureType]):
    width: int = 0
    height: int = 0
    mipmap_count: int = 0
    fourcc: bytes = field(default_factory=bytes)
    texture: TextureType = field(default_factory=lambda: cast(TextureType, DefaultTexture()))
    is_hdri: bool = False


@dataclass
class ImageContent(FileContent):
    image: bytes = field(default_factory=bytes)
