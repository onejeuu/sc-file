"""Library processing and conversion options."""

from dataclasses import dataclass
from typing import ClassVar, Literal, TypedDict

from scfile.enums import FileFormat


type OnConflict = Literal["overwrite", "rename", "skip"]
ON_CONFLICT_OPTIONS: tuple[OnConflict, ...] = ("overwrite", "rename", "skip")
"""Supported actions when an output path already exists."""

DEFAULT_MODEL_FORMAT = FileFormat.OBJ
"""Default output format when skeleton processing is disabled."""

DEFAULT_SKELETON_FORMAT = FileFormat.GLB
"""Default output format when skeleton processing is enabled."""


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

    model_format: FileFormat | None
    """Preferred output format for models. Defaults are selected when unset."""

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
        model_format: FileFormat | None = None,
        on_conflict: OnConflict = "overwrite",
    ) -> None:
        self.model = model if isinstance(model, ModelOptions) else ModelOptions(**(model or {}))
        self.region = region if isinstance(region, RegionOptions) else RegionOptions(**(region or {}))
        self.model_format = model_format
        self.on_conflict = on_conflict

    @property
    def default_format(self) -> FileFormat:
        """Default model output format for the current model options."""

        if self.model.skeleton_enabled:
            return DEFAULT_SKELETON_FORMAT

        return DEFAULT_MODEL_FORMAT
