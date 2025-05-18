"""
Dataclasses for skeletal animation (clips/actions).
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class AnimationClip:
    name: str = "clip"
    rate: float = 0.33
    frames: int = 0
    transforms: np.ndarray = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))

    @property
    def times(self):
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    clips: list[AnimationClip] = field(default_factory=list)
