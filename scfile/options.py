"""Shared options."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from scfile import content as C
from scfile.content.models import Feature, Features
from scfile.enums import FileFormat, OnConflict


DEFAULT_OUTPUT_FORMATS: dict[type[C.BaseContent], FileFormat] = {
    C.ModelContent: FileFormat.OBJ,
    C.TextureContent: FileFormat.DDS,
    C.ImageContent: FileFormat.PNG,
    C.ArchiveContent: FileFormat.ZIP,
    C.DocumentContent: FileFormat.JSON,
    C.RegionContent: FileFormat.MCA,
}
"""Default output formats by content type."""

SKELETON_TARGET = FileFormat.GLB
"""Default model target when skeleton processing is enabled."""

type OutputFormatConfig = Mapping[type[C.BaseContent], FileFormat]
"""Requested output formats by content type."""

type MdatVersion = Literal[5, 6, 7]
"""Supported MDAT format major versions."""

type BlockMapping = dict[str, str]
"""Source block ID strings mapped to target ID strings."""

type BlockMappings = tuple[BlockMapping, ...] | BlockMapping | None
"""One mapping or ordered mapping layers. Normalized to a tuple by Options."""


@dataclass
class Options:
    """Options for library handlers and conversion operations."""

    output_formats: OutputFormatConfig = field(default_factory=dict)
    """Normalized output format for every content type."""

    on_conflict: OnConflict = OnConflict.REPLACE
    """
    Action when an output file already exists.

    - `"replace"` Replace the existing file
    - `"rename"` Add a numeric suffix (e.g. `model (1).obj`)
    - `"skip"` Keep the existing file
    """

    skeleton: bool = False
    """Handle skeleton bones from models."""

    animation: bool = False
    """Handle built-in animation clips from models."""

    ol_max_mipmaps: int | None = None
    """Maximum texture mipmaps to decode. Use zero to parse header metadata only."""

    mcal_filtering: bool = True
    """Filter technical and duplicate clips from MCAL animations."""

    mdat_version: MdatVersion | None = None
    """Major version of the MDAT source format."""

    mdat_biomes: bool = True
    """Export biome data from MDAT chunks."""

    mdat_materials: bool = True
    """Apply material records from MDAT chunks to world terrain."""

    mdat_objects: bool = False
    """Parse objects from MDAT chunks."""

    mca_mappings: BlockMappings = None
    """Ordered block mapping layers for MCA terrain."""

    mca_backup: bool = True
    """Keep the original MCA region before replacement."""

    def __post_init__(self) -> None:
        defaults = dict(DEFAULT_OUTPUT_FORMATS)
        if self.skeleton_enabled:
            defaults[C.ModelContent] = SKELETON_TARGET

        defaults.update(self.output_formats)
        self.output_formats = defaults

        self.on_conflict = OnConflict(self.on_conflict)

        if self.ol_max_mipmaps is not None:
            self.ol_max_mipmaps = max(0, self.ol_max_mipmaps)

        if self.mca_mappings is None:
            self.mca_mappings = ()
        elif isinstance(self.mca_mappings, Mapping):
            self.mca_mappings = (self.mca_mappings,)
        else:
            self.mca_mappings = tuple(self.mca_mappings)

    @property
    def skeleton_enabled(self) -> bool:
        """Return whether skeleton data is needed."""

        return self.skeleton or self.animation

    @property
    def mdat_materials_only(self) -> bool:
        return self.mdat_materials and not self.mdat_objects

    @property
    def model_features(self) -> Features:
        """Features requested for model processing."""

        features: Features = ()
        if self.skeleton_enabled:
            features += (Feature.SKELETON,)

        if self.animation:
            features += (Feature.ANIMATION,)

        return features
