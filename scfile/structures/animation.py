"""
Dataclasses for skeletal animation (clips/actions).
"""

from dataclasses import dataclass, field

import numpy as np

from .skeleton import ModelSkeleton


@dataclass
class AnimationClip:
    """Single animation clip with timing and transformation data."""

    name: str = "clip"
    frames: int = 0
    rate: float = 0.33
    transforms: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float32))

    @property
    def times(self):
        return np.arange(self.frames, dtype=np.float32) * self.rate


@dataclass
class ModelAnimation:
    """Animation clips container."""

    clips: list[AnimationClip] = field(default_factory=list)

    def convert_to_local(self, skeleton: ModelSkeleton):
        for clip in self.clips:
            for bone in skeleton.bones:
                clip.transforms[:, bone.id, 4:7] += bone.position
