"""
Conversion by input path. Optional output folder and options.
"""

import pathlib
from typing import Callable, Optional, TypeAlias

import lz4.block

from scfile.core.context import UserOptions
from scfile.core.types import PathLike
from scfile.enums import FileFormat
from scfile.exceptions.io import InvalidStructureError, UnsupportedFormatError

from . import formats, legacy


ModelConverters: TypeAlias = dict[FileFormat, Callable]


# TODO: improve this

MCSB_CONVERTERS: ModelConverters = {
    FileFormat.DAE: formats.mcsb_to_dae,
    FileFormat.OBJ: formats.mcsb_to_obj,
    FileFormat.GLB: formats.mcsb_to_glb,
    FileFormat.MS3D: formats.mcsb_to_ms3d,
}

MCSA_CONVERTERS: ModelConverters = {
    FileFormat.DAE: legacy.mcsa_to_dae,
    FileFormat.OBJ: legacy.mcsa_to_obj,
    FileFormat.GLB: legacy.mcsa_to_glb,
    FileFormat.MS3D: legacy.mcsa_to_ms3d,
}

MODEL_CONVERTERS: dict[FileFormat, ModelConverters] = {
    FileFormat.MCSB: MCSB_CONVERTERS,
    FileFormat.MCSA: MCSA_CONVERTERS,
    FileFormat.MCVD: MCSA_CONVERTERS,
}


def auto(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    src_path = pathlib.Path(source)
    src_format = src_path.suffix.lstrip(".")

    options = options or UserOptions()
    model_formats = options.model_formats or options.default_model_formats

    match src_format:
        case FileFormat.MCSA | FileFormat.MCSB | FileFormat.MCVD:
            converter_map = MODEL_CONVERTERS[src_format]
            for fmt in model_formats:
                # TODO: typehints
                if converter := converter_map.get(fmt):
                    converter(source, output, options)

        case FileFormat.OL:
            try:
                formats.ol_to_dds(source, output, options)

            except lz4.block.LZ4BlockError:
                try:
                    formats.ol_cubemap_to_dds(source, output, options)

                except lz4.block.LZ4BlockError as err:
                    raise InvalidStructureError(source) from err

        case FileFormat.MIC:
            formats.mic_to_png(source, output, options)

        case _:
            raise UnsupportedFormatError(src_path)
