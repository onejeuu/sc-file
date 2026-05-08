from dataclasses import dataclass, field
from pathlib import Path

from scfile.consts import NBT_FILENAMES
from scfile.enums import FileFormat

from .strings import Strings


DEFAULT_OUTPUT = Path.home() / "scfile" / "export"


@dataclass
class Feature:
    id: str
    icon: str
    label: str

    @property
    def title(self) -> str:
        return f"{self.icon} {self.label}"


class FT:
    SKELETON = Feature("skeleton", "🦴", Strings.get("feat_skeleton"))
    ANIMATION = Feature("animation", "🌀", Strings.get("feat_animation"))


@dataclass
class FileKind:
    id: str
    icon: str
    label: str
    suffixes: list[str]
    features: list[Feature] = field(default_factory=list)

    @property
    def title(self) -> str:
        return f"{self.icon} {self.label}"

    @property
    def feature_map(self) -> dict[str, str]:
        return {f.id: f.title for f in self.features}


FILE_KINDS: list[FileKind] = [
    FileKind(
        "models",
        "🧊",
        Strings.get("fmt_models"),
        suffixes=[".mcsa", ".mcsb", ".mcvd"],
        features=[FT.SKELETON, FT.ANIMATION],
    ),
    FileKind(
        "textures",
        "🧱",
        Strings.get("fmt_textures"),
        suffixes=[".ol"],
    ),
    FileKind(
        "images",
        "🖼",
        Strings.get("fmt_images"),
        suffixes=[".mic"],
    ),
    FileKind(
        "texarr",
        "🗃️",
        Strings.get("fmt_texarr"),
        suffixes=[".texarr"],
    ),
    FileKind(
        "nbt",
        "⚙️",
        Strings.get("fmt_nbt"),
        suffixes=list(sorted(NBT_FILENAMES)),
    ),
]


@dataclass
class ModelFormat:
    id: FileFormat
    features: list[Feature] = field(default_factory=list)

    def __str__(self) -> str:
        icons = " ".join(f.icon for f in self.features)
        return f"{self.id.upper()} {icons}".strip()


MODEL_FORMATS = [
    ModelFormat(FileFormat.OBJ),
    ModelFormat(FileFormat.GLB, features=[FT.SKELETON, FT.ANIMATION]),
    ModelFormat(FileFormat.FBX, features=[FT.SKELETON]),
    ModelFormat(FileFormat.DAE, features=[FT.SKELETON]),
    ModelFormat(FileFormat.MS3D, features=[FT.SKELETON]),
]
