"""Shared options."""

from dataclasses import dataclass, field
from typing import Mapping

from scfile import content as C
from scfile.content.models import Feature, Features
from scfile.enums import FileFormat, OnConflict


DEFAULT_TARGETS: dict[type[C.BaseContent], FileFormat] = {
    C.ModelContent: FileFormat.OBJ,
    C.TextureContent: FileFormat.DDS,
    C.ImageContent: FileFormat.PNG,
    C.ArchiveContent: FileFormat.ZIP,
    C.DocumentContent: FileFormat.JSON,
    C.RegionContent: FileFormat.MCA,
}
"""Default conversion targets by content type."""

SKELETON_TARGET = FileFormat.GLB
"""Default model target when skeleton processing is enabled."""

type TargetConfig = Mapping[type[C.BaseContent], FileFormat]
"""Requested conversion targets by content type."""


@dataclass
class Options:
    """Options for library handlers and conversion operations."""

    skeleton: bool = False
    """Handle skeleton bones from models."""

    animation: bool = False
    """Handle built-in animation clips from models."""

    preserve_clips: bool = False
    """Keep all clips from animation library."""

    biomes: bool = True
    """Export biome data for world regions."""

    backup_regions: bool = True
    """Keep original world region."""

    extended_chunk: bool = False
    """Expose auxiliary world chunk data."""

    targets: TargetConfig = field(default_factory=dict)
    """Normalized output format for every content type."""

    on_conflict: OnConflict = OnConflict.REPLACE
    """
    Action when an output file already exists.

    - `"replace"` Replace the existing file
    - `"rename"` Add a numeric suffix (e.g. `model (1).obj`)
    - `"skip"` Keep the existing file
    """

    max_mipmaps: int | None = None
    """Maximum texture mipmaps to decode. Use zero to parse metadata only."""

    def __post_init__(self) -> None:
        self.on_conflict = OnConflict(self.on_conflict)

        if self.max_mipmaps is not None:
            self.max_mipmaps = max(0, self.max_mipmaps)

        defaults = dict(DEFAULT_TARGETS)
        if self.skeleton_enabled:
            defaults[C.ModelContent] = SKELETON_TARGET

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
