from dataclasses import dataclass, field
from pathlib import Path

from scfile.consts import SUPPORTED_NBT
from scfile.enums import FileFormat

from . import strings


TITLE = "scfile"
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
    SKELETON = Feature(id="skeleton", icon="🦴", label=strings.get("feature.skeleton"))
    ANIMATION = Feature(id="animation", icon="🌀", label=strings.get("feature.animation"))


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
        suffixes=list(sorted(SUPPORTED_NBT)),
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
    ModelFormat(FileFormat.DAE, features=[FT.SKELETON]),
    ModelFormat(FileFormat.MS3D, features=[FT.SKELETON]),
    ModelFormat(FileFormat.FBX),
]
