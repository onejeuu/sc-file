"""Shared options."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

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

type MdatVersion = Literal[5, 6, 7]
"""Supported MDAT format major versions."""

type BlockMapping = Mapping[int, int]
"""A partial mapping from source block IDs to target block IDs."""

type BlockMappings = tuple[BlockMapping, ...] | BlockMapping | None
"""One mapping or ordered mapping layers. Normalized to a tuple by Options."""


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
    """Expose records and objects from world chunks."""

    block_mappings: BlockMappings = None
    """Ordered block mapping layers. Empty means the built-in resource-pack mapping."""

    mdat_version: MdatVersion | None = None
    """Major version of the MDAT source format."""

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

        if self.block_mappings is None:
            self.block_mappings = ()
        elif isinstance(self.block_mappings, Mapping):
            self.block_mappings = (self.block_mappings,)
        else:
            self.block_mappings = tuple(self.block_mappings)

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
