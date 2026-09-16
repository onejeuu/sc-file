from dataclasses import dataclass

from scfile.app.consts import MODEL_FORMAT_ORDER
from scfile.content import BaseContent, ModelContent
from scfile.core import ModelEncoder
from scfile.enums import FileFormat
from scfile.formats import registry


@dataclass(frozen=True, slots=True)
class FormatGroup:
    name: str
    label: str
    display: tuple[str, ...]
    formats: tuple[FileFormat, ...]

    @property
    def filters(self) -> tuple[str, ...]:
        return tuple(sorted(registry.filters(*self.formats)))

    @property
    def content_type(self) -> type[BaseContent]:
        return registry.decoders[self.formats[0]].content_type


FORMAT_GROUPS = (
    FormatGroup(
        name="models",
        label="format.models",
        display=(".mcsb", ".mcvd", ".efkmodel"),
        formats=(FileFormat.MCSA, FileFormat.MCSB, FileFormat.MCVD, FileFormat.EFKMODEL),
    ),
    FormatGroup(
        name="textures",
        label="format.textures",
        display=(".ol",),
        formats=(FileFormat.OL,),
    ),
    FormatGroup(
        name="images",
        label="format.images",
        display=(".mic",),
        formats=(FileFormat.MIC,),
    ),
    FormatGroup(
        name="archive",
        label="format.archive",
        display=(".texarr",),
        formats=(FileFormat.TEXARR,),
    ),
    FormatGroup(
        name="documents",
        label="format.documents",
        display=("itemnames.dat", "sd0-4"),
        formats=(FileFormat.NBT, FileFormat.MAP),
    ),
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
