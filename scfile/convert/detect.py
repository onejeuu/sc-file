"""
Format auto-detection by file extension.
"""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.consts import SUPPORTED_NBT
from scfile.core import Options
from scfile.enums import FileFormat

from . import factory, formats


def format(
    source: types.PathLike,
) -> str:
    """Detect input file format."""
    path = Path(source)

    if path.name.lower() in SUPPORTED_NBT:
        return str(FileFormat.NBT)

    return path.suffix.lower().lstrip(".")


def auto(
    source: types.PathLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> None:
    """
    Automatically convert one file between formats based on its extension.

    Arguments:
        source: Path to source file.
        output (optional): Path to directory. Defaults to same location as source.
        options (optional): Shared handlers options.

    Raises:
        InvalidStructureError: Source file is corrupted.
        UnsupportedFormatError: Source file format not supported.

    Example:
        - ``auto("model.mcsb", "model.obj")``
        - ``auto("model.mcsb", "model.obj", Options(skeleton=True))``
        - ``auto("model.mcsb", "path/to/output/dir")``
    """

    src_path = Path(source)
    src_format = format(source)

    options = options or Options()
    model_formats = options.model_formats or options.default_model_formats

    # Detect format by file suffix
    match src_format:
        case FileFormat.MCSB | FileFormat.MCSA | FileFormat.MCVD | FileFormat.EFKMODEL:
            # Get converters mapping from mapping
            converters = factory.converters(src_format)

            # Convert model to all requested formats
            for fmt in model_formats:
                converters[fmt](source, output, options)

        case FileFormat.OL:
            formats.ol_to_dds(source, output, options)

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
