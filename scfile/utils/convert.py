from pathlib import Path
from typing import Optional, TypeVar

from scfile import exceptions as exc
from scfile.enums import FileSuffix
from scfile.file.base import FileDecoder, FileEncoder
from scfile.file.data.base import FileData
from scfile.file.formats.dae import DaeEncoder
from scfile.file.formats.dds import DdsEncoder
from scfile.file.formats.mcsa import McsaDecoder
from scfile.file.formats.mic import MicDecoder
from scfile.file.formats.ms3d import Ms3dBinEncoder
from scfile.file.formats.ms3d_ascii import Ms3dAsciiEncoder
from scfile.file.formats.obj import ObjEncoder
from scfile.file.formats.ol import OlDecoder
from scfile.file.formats.png import PngEncoder
from scfile.io.binary import BinaryFileIO
from scfile.utils.types import PathLike


OPENER = TypeVar("OPENER", bound=BinaryFileIO)
DATA = TypeVar("DATA", bound=FileData)


def mcsa_to_dae(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting model `.mcsa` file to `.dae`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output `.dae` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_dae("model.mcsa", "model.dae")`
    """

    _convert(source, output, McsaDecoder, DaeEncoder, FileSuffix.DAE)


def mcsa_to_ms3d(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting model `.mcsa` file to `.ms3d`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output `.ms3d` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_ms3d("model.mcsa", "model.ms3d")`
    """

    _convert(source, output, McsaDecoder, Ms3dBinEncoder, FileSuffix.MS3D)


def mcsa_to_ms3d_ascii(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting model `.mcsa` file to `.txt`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output `.txt` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_ms3d_ascii("model.mcsa", "model.txt")`
    """

    _convert(source, output, McsaDecoder, Ms3dAsciiEncoder, FileSuffix.TXT)


def mcsa_to_obj(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting model `.mcsa` file to `.obj`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output `.obj` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_obj("model.mcsa", "model.obj")`
    """

    _convert(source, output, McsaDecoder, ObjEncoder, FileSuffix.OBJ)


def mic_to_png(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting image `.mic` file to `.png`.

    Args:
        source: Path to `.mic` file.
        output (optional): Path to output `.png` file.
        Defaults to source path with new suffix.

    Example:
        `mic_to_png("image.mic", "image.png")`
    """

    _convert(source, output, MicDecoder, PngEncoder, FileSuffix.PNG)


def ol_to_dds(source: PathLike, output: Optional[PathLike] = None):
    """
    Converting texture `.ol` file to `.dds`.

    Args:
        source: Path to `.ol` file.
        output (optional): Path to output `.dds` file.
        Defaults to source path with new suffix.

    Example:
        `ol_to_dds("texture.ol", "texture.dds")`
    """

    _convert(source, output, OlDecoder, DdsEncoder, FileSuffix.DDS)


def auto(source: PathLike, output: Optional[PathLike] = None):
    """
    Automatically determines which format convert to.

    Args:
        source: Path to encrypted file.
        output (optional): Path to output decrypted file.
        Defaults to source path with new suffix.

    Raises:
        FileSuffixUnsupported - if source suffix not in consts.SUPPORTED_SUFFIXES.

    Example:
        `auto("file.mic", "file.png")`
    """

    path = Path(source)

    match path.suffix.lstrip("."):
        case FileSuffix.MCSA | FileSuffix.MCVD:
            mcsa_to_obj(source, output)
            mcsa_to_ms3d(source, output)

        case FileSuffix.MIC:
            mic_to_png(source, output)

        case FileSuffix.OL:
            ol_to_dds(source, output)

        case _:
            raise exc.FileSuffixUnsupported(path)


def _convert(
    source: PathLike,
    output: Optional[PathLike],
    decoder: type[FileDecoder[OPENER, DATA]],
    encoder: type[FileEncoder[DATA]],
    new_suffix: str,
):
    src = Path(source)
    new_src = src.with_suffix(f".{new_suffix}")

    dest = Path(output) if output else new_src

    # Check that file exists
    if not src.exists() or not src.is_file():
        raise exc.FileNotFound(src)

    # If destination is directory save file in this directory
    if dest.is_dir():
        dest = Path(dest, new_src.name)

    # Convert and save file
    with decoder(src) as dec:
        dec.convert_to(encoder).save(dest)
