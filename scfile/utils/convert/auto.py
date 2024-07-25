from pathlib import Path
from typing import Optional, Sequence

from scfile import exceptions as exc
from scfile.enums import FileSuffix
from scfile.utils.types import PathLike

from . import formats as convert


DEFAULT_MODEL_FORMATS = (FileSuffix.OBJ,)

MODEL_CONVERTER_MAP = {
    FileSuffix.DAE: convert.mcsa_to_dae,
    FileSuffix.OBJ: convert.mcsa_to_obj,
    FileSuffix.MS3D: convert.mcsa_to_ms3d,
    FileSuffix.MS3D_ASCII: convert.mcsa_to_ms3d_ascii,
}


def auto(
    source: PathLike,
    output: Optional[PathLike] = None,
    formats: Optional[Sequence[FileSuffix]] = None,
    overwrite: bool = True,
    hdri: bool = False,
):
    """
    Automatically determines which format convert to.

    Args:
        source: Path to encrypted file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        formats (optional): Sequence of FileSuffix for preferred output models formats.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.
        hdri (optional): Convert ol texture as hdri sky. Defaults to False.

    Raises:
        FileSuffixUnsupported - if source suffix not in consts.SUPPORTED_SUFFIXES.

    Example:
        `auto("file.mcsa")`
    """

    if not formats:
        formats = DEFAULT_MODEL_FORMATS

    path = Path(source)
    suffix = path.suffix.lstrip(".")

    args = (source, output, overwrite)

    match suffix:
        case FileSuffix.MCSA | FileSuffix.MCVD:
            for fmt in formats:
                if converter := MODEL_CONVERTER_MAP.get(fmt):
                    converter(*args)

        case FileSuffix.MIC:
            convert.mic_to_png(*args)

        case FileSuffix.OL:
            if hdri:
                convert.ol_hdri_to_dds(*args)
                return

            convert.ol_to_dds(*args)

        case _:
            raise exc.FileSuffixUnsupported(path)
