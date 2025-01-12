import pathlib
from typing import Callable, Optional, Sequence, TypeAlias

from scfile.core.options import ImageOptions, ModelOptions, TextureOptions
from scfile.enums import FileFormat
from scfile.io.types import PathLike

from . import formats


ModelFormats: TypeAlias = Sequence[FileFormat]

DEFAULT_MODEL_FORMATS: ModelFormats = (FileFormat.DAE,)

MODEL_CONVERTER_MAP: dict[FileFormat, Callable] = {
    FileFormat.DAE: formats.mcsa_to_dae,
    FileFormat.OBJ: formats.mcsa_to_obj,
    FileFormat.GLB: formats.mcsa_to_gltf,
    FileFormat.MS3D: formats.mcsa_to_ms3d,
}


def auto(
    source: PathLike,
    output: Optional[PathLike] = None,
    model_options: Optional[ModelOptions] = None,
    texture_options: Optional[TextureOptions] = None,
    image_options: Optional[ImageOptions] = None,
    overwrite: bool = True,
    model_formats: Optional[ModelFormats] = None,
):
    src_path = pathlib.Path(source)
    src_format = src_path.suffix.lstrip(".")

    model_formats = model_formats or DEFAULT_MODEL_FORMATS

    match src_format:
        case FileFormat.MCSA | FileFormat.MCVD:
            for fmt in model_formats:
                if converter := MODEL_CONVERTER_MAP.get(fmt):
                    converter(source, output, model_options, overwrite)

        case FileFormat.OL:
            formats.ol_to_dds(source, output, texture_options, overwrite)

        case FileFormat.MIC:
            formats.mic_to_png(source, output, image_options, overwrite)

        case _:
            raise Exception("File suffix not supported")
