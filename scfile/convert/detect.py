"""
Conversion by input path based on file suffix.
"""

import pathlib
from collections import deque
from typing import Callable, Optional, TypeAlias

import lz4.block

from scfile import exceptions
from scfile.consts import NBT_FILENAMES
from scfile.core import UserOptions
from scfile.enums import FileFormat
from scfile.types import OutputDir, PathLike

from . import formats, legacy


ConvertersMap: TypeAlias = dict[FileFormat, Callable]


MCSB: ConvertersMap = {
    FileFormat.OBJ: formats.mcsb_to_obj,
    FileFormat.GLB: formats.mcsb_to_glb,
    FileFormat.DAE: formats.mcsb_to_dae,
    FileFormat.MS3D: formats.mcsb_to_ms3d,
}

MCSA: ConvertersMap = {
    FileFormat.OBJ: legacy.mcsa_to_obj,
    FileFormat.GLB: legacy.mcsa_to_glb,
    FileFormat.DAE: legacy.mcsa_to_dae,
    FileFormat.MS3D: legacy.mcsa_to_ms3d,
}


def auto(
    source: PathLike,
    output: OutputDir = None,
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

    # Detect format by file suffix
    match src_format:
        case FileFormat.MCSB:
            # Convert MCSB to all requested formats.
            deque(map(lambda fmt: MCSB[fmt](source, output, options), model_formats), maxlen=0)

        case FileFormat.MCSA | FileFormat.MCVD:
            # Convert MCSA to all requested formats.
            deque(map(lambda fmt: MCSA[fmt](source, output, options), model_formats), maxlen=0)

        case FileFormat.OL:
            # Try standard texture first.
            try:
                formats.ol_to_dds(source, output, options)

            except lz4.block.LZ4BlockError:
                # Fallback to cubemap on failure.
                try:
                    formats.ol_cubemap_to_dds(source, output, options)

                except lz4.block.LZ4BlockError as err:
                    raise exceptions.InvalidStructureError(source) from err

        case FileFormat.MIC:
            formats.mic_to_png(source, output, options)

        case FileFormat.TEXARR:
            formats.texarr_to_zip(source, output, options)

        case FileFormat.NBT:
            formats.nbt_to_json(source, output, options)

        case _:
            # Detect nbt by file name
            if src_path.name in NBT_FILENAMES:
                formats.nbt_to_json(source, output, options)
                return

            raise exceptions.UnsupportedFormatError(src_path)
