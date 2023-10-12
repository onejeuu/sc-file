from pathlib import Path
from typing import Optional

from scfile import exceptions as exc
from scfile.consts import FileSuffix
from scfile.files import McsaFile, MicFile, OlFile
from scfile.files.source.base import BaseSourceFile
from scfile.utils.reader import BinaryReader


StringOrPath = str | Path


def mcsa_to_obj(source: StringOrPath, output: Optional[StringOrPath] = None):
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


def mic_to_png(source: StringOrPath, output: Optional[StringOrPath] = None):
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


def ol_to_dds(source: StringOrPath, output: Optional[StringOrPath] = None):
    """
    Converting `.ol` file to `.dds`.

    Args:
        source: Full path to `.ol` file.
        output (optional): Full path to output `.dds` file.
        Defaults to source path with new suffix.

    Example:
        `ol_to_dds("C:/file.ol", "C:/file.dds")`
    """

    _convert(source, output, OlFile, FileSuffix.DDS)


def auto(source: StringOrPath, output: Optional[StringOrPath] = None):
    """
    Automatically determines which format convert to.

    Args:
        source: Full path to encrypted file.
        output (optional): Full path to output decrypted file.
        Defaults to source path with new suffix.

    Raises:
        UnsupportedFormat - if source suffix not in `.mic`, `.ol`, `.mcsa`.

    Example:
        `auto("C:/file.mic", "C:/file.png")`
    """

    source_path = Path(source)

    match source_path.suffix:
        case FileSuffix.MIC:
            mic_to_png(source, output)

        case FileSuffix.OL:
            ol_to_dds(source, output)

        case FileSuffix.MCSA:
            mcsa_to_obj(source, output)

        case _:
            raise exc.UnsupportedFormat(f"File '{source_path.as_posix()}' unsupported.")


def _convert(
    source: StringOrPath,
    output: Optional[StringOrPath],
    converter: type[BaseSourceFile],
    suffix: str
):
    src = Path(source)
    dest = Path(output) if output else src.with_suffix(suffix)

    if not src.exists() or not src.is_file():
        raise exc.SourceFileNotFound(f"File '{src.as_posix()}' not found.")

    with BinaryReader(src) as reader:
        converted = converter(reader).convert()

    with open(dest, "wb") as f:
        f.write(converted)
