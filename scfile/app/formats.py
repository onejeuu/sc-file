from scfile.app.consts import MODEL_FORMAT_ORDER
from scfile.enums import FileFormat
from scfile.registry import REGISTRY


def model_formats() -> tuple[FileFormat, ...]:
    available = REGISTRY.model_formats
    preferred = tuple(fmt for fmt in MODEL_FORMAT_ORDER if fmt in available)
    remaining = tuple(sorted(available.difference(MODEL_FORMAT_ORDER)))
    return (*preferred, *remaining)
