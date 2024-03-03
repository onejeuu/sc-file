from pathlib import Path
from typing import Optional

from scfile import exceptions as exc
from scfile.enums import FileSuffix
from scfile.file.dds.encoder import DdsEncoder
from scfile.file.decoder import FileDecoder
from scfile.file.encoder import FileEncoder
from scfile.file.mcsa.decoder import McsaDecoder
from scfile.file.mic.decoder import MicDecoder
from scfile.file.obj.encoder import ObjEncoder
from scfile.file.ol.decoder import OlDecoder
from scfile.file.png.encoder import PngEncoder
from scfile.types import PathLike


def mcsa_to_obj(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting `.mcsa` file to `.obj`.

    Args:
        source: Full path to `.mcsa` file.
        output (optional): Full path to output `.obj` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_obj("C:/file.mcsa", "C:/file.obj")`
    """

    _convert(source, output, McsaDecoder, ObjEncoder, FileSuffix.OBJ)


def mic_to_png(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting `.mic` file to `.png`.

    Args:
        source: Full path to `.mic` file.
        output (optional): Full path to output `.png` file.
        Defaults to source path with new suffix.

    Example:
        `mic_to_png("C:/file.mic", "C:/file.png")`
    """

    _convert(source, output, MicDecoder, PngEncoder, FileSuffix.PNG)


def ol_to_dds(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting `.ol` file to `.dds`.

    Args:
        source: Full path to `.ol` file.
        output (optional): Full path to output `.dds` file.
        Defaults to source path with new suffix.

    Example:
        `ol_to_dds("C:/file.ol", "C:/file.dds")`
    """

    _convert(source, output, OlDecoder, DdsEncoder, FileSuffix.DDS)


def auto(source: PathLike, output: Optional[PathLike] = None):
    """
    Automatically determines which format convert to.

    Args:
        source: Full path to encrypted file.
        output (optional): Full path to output decrypted file.
        Defaults to source path with new suffix.

    Raises:
        UnsupportedSuffix - if source suffix not in `.mic`, `.ol`, `.mcsa`.

    Example:
        `auto("C:/file.mic", "C:/file.png")`
    """

    path = Path(source)

    match path.suffix.lstrip("."):
        case FileSuffix.MIC:
            mic_to_png(source, output)

        case FileSuffix.OL:
            ol_to_dds(source, output)

        case FileSuffix.MCSA:
            mcsa_to_obj(source, output)

        case _:
            raise exc.UnsupportedSuffix(path)


# TODO: Fix type hints
def _convert(
    source: PathLike,
    output: Optional[PathLike],
    decoder: type[FileDecoder],
    encoder: type[FileEncoder],
    new_suffix: str,
):
    src = Path(source)
    new_src = src.with_suffix(f".{new_suffix}")

    dest = Path(output) if output else new_src

    # Check that file exists
    if not src.exists() or not src.is_file():
        raise exc.SourceFileNotFound(src)

    # If destination is directory save file in this folder
    if dest.is_dir():
        dest = Path(dest, new_src.name)

    # Convert and save file
    with decoder(src) as dec:
        dec.convert(encoder).save(dest)
