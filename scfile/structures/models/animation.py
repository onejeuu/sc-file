from dataclasses import dataclass, field

import numpy as np

from .enums import AnimationRotation, AnimationTranslation
from .types import AnimationRotations, AnimationTimes, AnimationTranslations


@dataclass
class AnimationClip:
    """Single animation clip with timing and transformation data."""

    name: str = "clip"
    frames: int = 0
    rate: float = 0.33
    translations: AnimationTranslations = field(default_factory=lambda: np.zeros(0, dtype=np.float32))
    rotations: AnimationRotations = field(default_factory=lambda: np.zeros(0, dtype=np.float32))

    @property
    def times(self) -> AnimationTimes:
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    """Animation clips container."""

    clips: list[AnimationClip] = field(default_factory=list)
    translation: AnimationTranslation = AnimationTranslation.DELTA
    rotation: AnimationRotation = AnimationRotation.QUATERNION
