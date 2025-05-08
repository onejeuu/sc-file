"""
Conversion by input path. Optional output folder, options and preferred formats.
"""

import pathlib
from typing import Callable, Optional, Sequence, TypeAlias

from scfile import exceptions as exc
from scfile.core.context import ImageOptions, ModelOptions, TextureOptions
from scfile.core.types import PathLike
from scfile.enums import FileFormat

from . import formats


ModelFormats: TypeAlias = Sequence[FileFormat]
ModelConverters: TypeAlias = dict[FileFormat, Callable]

DEFAULT_MODEL_FORMATS: ModelFormats = (FileFormat.OBJ,)
DEFAULT_SKELETON_MODEL_FORMATS: ModelFormats = (FileFormat.GLB,)


# TODO: global converter map?

MCSB_CONVERTERS: ModelConverters = {
    FileFormat.DAE: formats.mcsb_to_dae,
    FileFormat.OBJ: formats.mcsb_to_obj,
    FileFormat.GLB: formats.mcsb_to_gltf,
    FileFormat.MS3D: formats.mcsb_to_ms3d,
}

MCSA_CONVERTERS: ModelConverters = {
    FileFormat.DAE: formats.mcsa_to_dae,
    FileFormat.OBJ: formats.mcsa_to_obj,
    FileFormat.GLB: formats.mcsa_to_gltf,
    FileFormat.MS3D: formats.mcsa_to_ms3d,
}

MODEL_CONVERTERS: dict[FileFormat, ModelConverters] = {
    FileFormat.MCSB: MCSB_CONVERTERS,
    FileFormat.MCSA: MCSA_CONVERTERS,
    FileFormat.MCVD: MCSA_CONVERTERS,
}


def auto(
    source: PathLike,
    output: Optional[PathLike] = None,
    model_options: Optional[ModelOptions] = None,
    texture_options: Optional[TextureOptions] = None,
    image_options: Optional[ImageOptions] = None,
    model_formats: Optional[ModelFormats] = None,
    overwrite: bool = True,
):
    src_path = pathlib.Path(source)
    src_format = src_path.suffix.lstrip(".")

    default_formats = (
        DEFAULT_SKELETON_MODEL_FORMATS if model_options and model_options.parse_skeleton else DEFAULT_MODEL_FORMATS
    )
    model_formats = model_formats or default_formats

    match src_format:
        case FileFormat.MCSA | FileFormat.MCSB | FileFormat.MCVD:
            converter_map = MODEL_CONVERTERS[src_format]
            for target_fmt in model_formats:
                if converter := converter_map.get(target_fmt):
                    converter(source, output, model_options, overwrite)

        case FileFormat.OL:
            if texture_options and texture_options.is_hdri:
                formats.ol_hdri_to_dds(source, output, texture_options, overwrite)
            else:
                formats.ol_to_dds(source, output, texture_options, overwrite)

        case FileFormat.MIC:
            formats.mic_to_png(source, output, image_options, overwrite)

        case _:
            raise exc.FileSuffixUnsupported(src_path)
