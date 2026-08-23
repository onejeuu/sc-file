"""Source metadata for model content."""

from dataclasses import dataclass, field

from .counts import ModelCounts
from .enums import Feature
from .types import FeatureFlags


@dataclass
class ModelMeta:
    version: float = 0.0
    flags: FeatureFlags = field(default_factory=dict)
    counts: ModelCounts = field(default_factory=ModelCounts)

    def declares(self, feature: Feature) -> bool:
        """Return whether the source declares a model feature."""

        return bool(self.flags.get(feature))
