from dataclasses import dataclass

from scfile.app.consts import MODEL_FORMAT_ORDER
from scfile.core import ModelEncoder
from scfile.enums import FileFormat
from scfile.formats import registry
from scfile.structures.content import ModelContent
from scfile.structures.models import Feature


@dataclass(frozen=True, slots=True)
class FormatGroup:
    name: str
    icon: str
    label: str
    display: tuple[str, ...]
    formats: tuple[FileFormat, ...]
    features: tuple[Feature, ...] = ()

    @property
    def filters(self) -> tuple[str, ...]:
        return tuple(sorted(registry.filters(*self.formats)))


FORMAT_GROUPS = (
    FormatGroup(
        "models",
        "🧊",
        "format.models",
        (".mcsb", ".mcvd", ".efkmodel"),
        (FileFormat.MCSA, FileFormat.MCSB, FileFormat.MCVD, FileFormat.EFKMODEL),
        (Feature.SKELETON, Feature.ANIMATION),
    ),
    FormatGroup("textures", "🧱", "format.textures", (".ol",), (FileFormat.OL,)),
    FormatGroup("images", "🖼", "format.images", (".mic",), (FileFormat.MIC,)),
    FormatGroup("texarr", "🗃️", "format.texarr", (".texarr",), (FileFormat.TEXARR,)),
    FormatGroup("nbt", "⚙️", "format.nbt", ("itemnames.dat", "prefs", "sd1…sd4"), (FileFormat.NBT,)),
)


def model_formats() -> tuple[FileFormat, ...]:
    available = {
        format
        for format, encoder in registry.encoders.items()
        if encoder.content_type is ModelContent and issubclass(encoder, ModelEncoder)
    }
    preferred = tuple(fmt for fmt in MODEL_FORMAT_ORDER if fmt in available)
    remaining = tuple(sorted(available.difference(MODEL_FORMAT_ORDER)))
    return (*preferred, *remaining)
