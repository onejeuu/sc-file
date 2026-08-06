from dataclasses import dataclass, field

import numpy as np

from .enums import AnimationRotation, AnimationTranslation
from .types import AnimationRotations, AnimationTimes, AnimationTranslations, MorphWeights


@dataclass
class AnimationClip:
    """Keyframed bone and morph animation clip."""

    name: str = "clip"
    frames: int = 0
    rate: float = 0.33
    translations: AnimationTranslations = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))
    rotations: AnimationRotations = field(default_factory=lambda: np.zeros((0, 4), dtype=np.float32))
    morph_weights: MorphWeights = field(default_factory=lambda: np.zeros((0, 0), dtype=np.float32))

    @property
    def times(self) -> AnimationTimes:
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    """Animation clips container."""

    clips: list[AnimationClip] = field(default_factory=list)
    morph_channels: list[str] = field(default_factory=list)
    translation: AnimationTranslation = AnimationTranslation.DELTA
    rotation: AnimationRotation = AnimationRotation.QUATERNION
