from pathlib import Path
from typing import Optional, Type

from scfile import exceptions as exc
from scfile.consts import PathLike
from scfile.enums import FileSuffix
from scfile.files import McsaFile, MicFile, OlCubemapFile, OlFile
from scfile.files.source.base import BaseSourceFile


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

    _convert(source, output, McsaFile, FileSuffix.OBJ)


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

    _convert(source, output, MicFile, FileSuffix.PNG)


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

    try:
        _convert(source, output, OlFile, FileSuffix.DDS)

    except exc.OlInvalidFormat:
        _convert(source, output, OlCubemapFile, FileSuffix.DDS)


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


def _convert(
    source: PathLike,
    output: Optional[PathLike],
    converter: Type[BaseSourceFile],
    new_suffix: str
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

    # Get converted bytes using context manager
    with converter(src) as encrypted:
        converted = encrypted.convert()

    # Save converted bytes in destination file
    with open(dest, "wb") as fp:
        fp.write(converted)
