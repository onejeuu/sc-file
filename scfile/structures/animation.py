from dataclasses import dataclass, field

from .vectors import Quaternion, Vector3


@dataclass
class AnimationFrame:
    translation: Vector3 = field(default_factory=Vector3)
    rotation: Quaternion = field(default_factory=Quaternion)


@dataclass
class AnimationTransforms:
    frames: list[AnimationFrame] = field(default_factory=list)


@dataclass
class AnimationClip:
    name: str = "clip"
    rate: float = 0.33
    frames: int = 0
    transforms: list[AnimationTransforms] = field(default_factory=list)


@dataclass
class ModelAnimation:
    clips: list[AnimationClip] = field(default_factory=list)
