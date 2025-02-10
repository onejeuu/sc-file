from dataclasses import dataclass, field

from .vectors import Vector3, Vector4


@dataclass
class AnimationFrame:
    translation: Vector3 = field(default_factory=Vector3)
    rotation: Vector4 = field(default_factory=Vector4)


@dataclass
class AnimationClip:
    name: str = "clip"
    frames_count: int = 0
    frame_rate: float = 0.33
    frames: list[AnimationFrame] = field(default_factory=list)


@dataclass
class ModelAnimation:
    clips: list[AnimationClip] = field(default_factory=list)
