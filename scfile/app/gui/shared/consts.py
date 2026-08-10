from dataclasses import dataclass, field
from pathlib import Path

from scfile.enums import FileFormat
from scfile.registry import REGISTRY
from scfile.structures.models import Feature

from . import strings


TITLE = "scfile"
DEFAULT_OUTPUT = Path.home() / "scfile" / "export"


@dataclass
class FeatureView:
    """GUI presentation for model feature."""

    feature: Feature
    icon: str
    label: str

    @property
    def title(self) -> str:
        return f"{self.icon} {self.label}"


class FT:
    SKELETON = FeatureView(
        feature=Feature.SKELETON,
        icon="🦴",
        label=strings.get("feature.skeleton"),
    )
    ANIMATION = FeatureView(
        feature=Feature.ANIMATION,
        icon="🌀",
        label=strings.get("feature.animation"),
    )


FEATURE_VIEWS = (
    FT.SKELETON,
    FT.ANIMATION,
)


@dataclass
class FileKind:
    id: str
    icon: str
    label: str
    suffixes: list[str]
    features: list[FeatureView] = field(default_factory=list)

    @property
    def title(self) -> str:
        return f"{self.icon} {self.label}"

    @property
    def feature_map(self) -> dict[Feature, str]:
        return {view.feature: view.title for view in self.features}


FILE_KINDS: list[FileKind] = [
    FileKind(
        id="models",
        icon="🧊",
        label=strings.get("format.models"),
        suffixes=[".mcsa", ".mcsb", ".mcvd", ".efkmodel"],
        features=[FT.SKELETON, FT.ANIMATION],
    ),
    FileKind(
        id="textures",
        icon="🧱",
        label=strings.get("format.textures"),
        suffixes=[".ol"],
    ),
    FileKind(
        id="images",
        icon="🖼",
        label=strings.get("format.images"),
        suffixes=[".mic"],
    ),
    FileKind(
        id="texarr",
        icon="🗃️",
        label=strings.get("format.texarr"),
        suffixes=[".texarr"],
    ),
    FileKind(
        id="nbt",
        icon="⚙️",
        label=strings.get("format.nbt"),
        suffixes=sorted(REGISTRY.aliases_for(FileFormat.NBT)),
    ),
]


@dataclass
class ModelFormat:
    id: FileFormat

    def supports(
        self,
        feature: Feature,
    ) -> bool:
        return REGISTRY.model_supports(self.id, feature)

    def __str__(self) -> str:
        icons = " ".join(view.icon for view in FEATURE_VIEWS if self.supports(view.feature))
        return f"{self.id.upper()} {icons}".strip()


MODEL_FORMATS = [
    ModelFormat(FileFormat.OBJ),
    ModelFormat(FileFormat.GLB),
    ModelFormat(FileFormat.FBX),
]
