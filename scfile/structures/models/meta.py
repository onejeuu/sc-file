"""Source metadata for model content."""

from dataclasses import dataclass, field

from .counts import ModelCounts
from .types import FeatureFlags


@dataclass
class ModelMeta:
    version: float = 0.0
    flags: FeatureFlags = field(default_factory=dict)
    counts: ModelCounts = field(default_factory=ModelCounts)
