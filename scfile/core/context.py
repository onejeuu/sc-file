from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field

from scfile.utils.model.scene import ModelScene


class FileContext(ABC):
    pass


@dataclass
class ModelContext(FileContext):
    version: float = 0.0
    flags: defaultdict[int, bool] = field(default_factory=lambda: defaultdict(bool))
    scene: ModelScene = field(default_factory=ModelScene)

    @property
    def meshes(self):
        return self.scene.meshes

    @property
    def skeleton(self):
        return self.scene.skeleton
