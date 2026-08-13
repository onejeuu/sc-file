"""Library processing and conversion options."""

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import ClassVar, Literal, Mapping, Self, TypedDict

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

DEFAULT_TARGETS: Mapping[type[BaseContent], FileFormat] = MappingProxyType(
    {
        ModelContent: FileFormat.OBJ,
        TextureContent: FileFormat.DDS,
        ImageContent: FileFormat.PNG,
        ArchiveContent: FileFormat.ZIP,
        DocumentContent: FileFormat.JSON,
        RegionContent: FileFormat.MCA,
    }
)
"""Default conversion targets by content type."""

SKELETON_TARGET = FileFormat.GLB
"""Default model target when skeleton processing is enabled."""

type TargetConfig = Mapping[type[BaseContent], FileFormat]
"""Requested conversion targets by content type."""


class ModelConfig(TypedDict, total=False):
    skeleton: bool
    animation: bool


class RegionConfig(TypedDict, total=False):
    raw_blocks: bool
    full_chunk: bool


@dataclass
class ModelOptions:
    """Normalized model processing configuration."""

    skeleton: bool = False
    animation: bool = False

    @property
    def skeleton_enabled(self) -> bool:
        """Return whether skeleton data is needed."""

        return self.skeleton or self.animation

    @property
    def features(self) -> Features:
        """Features requested for model processing."""

        features: Features = ()
        if self.skeleton_enabled:
            features += (Feature.SKELETON,)

        if self.animation:
            features += (Feature.ANIMATION,)

        return features


@dataclass
class RegionOptions:
    """Normalized region processing configuration."""

    raw_blocks: bool = False
    full_chunk: bool = False


class Options:
    """Options for library handlers and conversion operations."""

    Model: ClassVar[type[ModelOptions]] = ModelOptions
    """Normalized model configuration."""

    Region: ClassVar[type[RegionOptions]] = RegionOptions
    """Normalized region configuration."""

    model: ModelOptions
    """
    Model content processing options.

    - `"skeleton"` Handle skeleton bones from models
    - `"animation"` Handle built-in animation clips from models
    """

    region: RegionOptions
    """
    Region content processing options.

    - `"raw_blocks"` Keep raw block IDs without lookup table replacement
    - `"full_chunk"` Handle full chunk data including metadata
    """

    targets: Mapping[type[BaseContent], FileFormat]
    """Normalized output format for every content type."""

    on_conflict: OnConflict
    """
    Action when an output file already exists.

    - `"overwrite"` Replace the existing file
    - `"skip"` Keep the existing file
    - `"rename"` Add a numeric suffix (e.g. `model (1).obj`)
    """

    def __init__(
        self,
        model: ModelConfig | ModelOptions | None = None,
        region: RegionConfig | RegionOptions | None = None,
        targets: TargetConfig | None = None,
        on_conflict: OnConflict = "overwrite",
    ) -> None:
        self.model = model if isinstance(model, ModelOptions) else ModelOptions(**(model or {}))
        self.region = region if isinstance(region, RegionOptions) else RegionOptions(**(region or {}))

        defaults = dict(DEFAULT_TARGETS)
        if self.model.skeleton_enabled:
            defaults[ModelContent] = SKELETON_TARGET

        if targets:
            defaults.update(targets)

        self.targets = MappingProxyType(defaults)
        self.on_conflict = on_conflict

    def copy(self) -> Self:
        """Create an independent copy of these options."""

        return type(self)(
            model=replace(self.model),
            region=replace(self.region),
            targets=self.targets,
            on_conflict=self.on_conflict,
        )
