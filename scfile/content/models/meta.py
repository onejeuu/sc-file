"""Source metadata for model content."""

from dataclasses import dataclass, field

from .enums import Feature
from .types import FeatureFlags


@dataclass
class ModelCounts:
    meshes: int = 0
    bones: int = 0
    channels: int = 0
    clips: int = 0


@dataclass
class MeshCounts:
    vertices: int = 0
    polygons: int = 0
    max_influences: int = 0
    local_bones: int = 0
    blend_shapes: int = 0


@dataclass
class ModelMeta:
    version: float = 0.0
    flags: FeatureFlags = field(default_factory=dict)
    counts: ModelCounts = field(default_factory=ModelCounts)

    def declares(self, feature: Feature) -> bool:
        """Return whether the source declares a model feature."""

        return bool(self.flags.get(feature))
