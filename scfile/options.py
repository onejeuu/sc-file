"""Library processing and conversion options."""

from dataclasses import dataclass, field
from typing import Literal, Mapping

from scfile.enums import FileFormat
from scfile.structures.content import (
    ArchiveContent,
    BaseContent,
    DocumentContent,
    ImageContent,
    ModelContent,
    RegionContent,
    TextureContent,
)
from scfile.structures.models import Feature, Features


type OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: tuple[OnConflict, ...] = ("overwrite", "rename", "skip")
"""Supported actions when an output path already exists."""

DEFAULT_TARGETS: dict[type[BaseContent], FileFormat] = {
    ModelContent: FileFormat.OBJ,
    TextureContent: FileFormat.DDS,
    ImageContent: FileFormat.PNG,
    ArchiveContent: FileFormat.ZIP,
    DocumentContent: FileFormat.JSON,
    RegionContent: FileFormat.MCA,
}
"""Default conversion targets by content type."""

SKELETON_TARGET = FileFormat.GLB
"""Default model target when skeleton processing is enabled."""

type TargetConfig = Mapping[type[BaseContent], FileFormat]
"""Requested conversion targets by content type."""


@dataclass
class Options:
    """Options for library handlers and conversion operations."""

    skeleton: bool = False
    """Handle skeleton bones from models."""

    animation: bool = False
    """Handle built-in animation clips from models."""

    raw_clips: bool = False
    """Keep technical clips in animation libraries."""

    raw_blocks: bool = False
    """Keep raw block IDs without lookup table replacement."""

    full_chunk: bool = False
    """Handle full chunk data including metadata."""

    targets: TargetConfig = field(default_factory=dict)
    """Normalized output format for every content type."""

    on_conflict: OnConflict = "overwrite"
    """
    Action when an output file already exists.

    - `"overwrite"` Replace the existing file
    - `"skip"` Keep the existing file
    - `"rename"` Add a numeric suffix (e.g. `model (1).obj`)
    """

    def __post_init__(self) -> None:
        defaults = dict(DEFAULT_TARGETS)
        if self.skeleton_enabled:
            defaults[ModelContent] = SKELETON_TARGET

        defaults.update(self.targets)
        self.targets = defaults

    @property
    def skeleton_enabled(self) -> bool:
        """Return whether skeleton data is needed."""

        return self.skeleton or self.animation

    @property
    def model_features(self) -> Features:
        """Features requested for model processing."""

        features: Features = ()
        if self.skeleton_enabled:
            features += (Feature.SKELETON,)

        if self.animation:
            features += (Feature.ANIMATION,)

        return features
