"""
Conversion by input path based on file suffix.
"""

import pathlib
from typing import Optional

import lz4.block

from scfile import exceptions, types
from scfile.consts import SUPPORTED_NBT
from scfile.core import UserOptions
from scfile.enums import FileFormat

from . import factory, formats


def auto(
    source: types.PathLike,
    output: types.OutputLike = None,
    options: Optional[UserOptions] = None,
) -> None:
    """
    Automatically convert file between formats based on file suffix.

    Arguments:
        source: Path to input file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `auto("model.mcsb", "path/to/output", UserOptions(parse_skeleton=True))`
    """

    src_path = pathlib.Path(source)
    src_format = src_path.suffix.lstrip(".")

    options = options or UserOptions()
    model_formats = options.model_formats or options.default_model_formats

    # Detect NBT by file name
    if src_path.name in SUPPORTED_NBT:
        src_format = str(FileFormat.NBT)

    # Normalize mcvd format (same as mcsa)
    if src_format == FileFormat.MCVD:
        src_format = str(FileFormat.MCSA)

    # Detect format by file suffix
    match src_format:
        case FileFormat.MCSB | FileFormat.MCSA | FileFormat.MCVD | FileFormat.EFKMODEL:
            # Get converters mapping from mapping
            converters = factory.converters(src_format)

            # Convert model to all requested formats
            for fmt in model_formats:
                converters[fmt](source, output, options)

        case FileFormat.OL:
            # Try standard texture first
            try:
                formats.ol_to_dds(source, output, options)

            except lz4.block.LZ4BlockError:
                # Fallback to cubemap on failure
                try:
                    formats.ol_cubemap_to_dds(source, output, options)

                except lz4.block.LZ4BlockError as err:
                    raise exceptions.InvalidStructureError(str(source)) from err

        case FileFormat.MIC:
            formats.mic_to_png(source, output, options)

        case FileFormat.TEXARR:
            formats.texarr_to_zip(source, output, options)

        case FileFormat.NBT:
            formats.nbt_to_json(source, output, options)

        case FileFormat.MDAT:
            formats.mdat_to_mca(source, output, options)

        case _:
            raise exceptions.UnsupportedFormatError(str(src_path), src_path.suffix)
