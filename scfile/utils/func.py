from pathlib import Path
from typing import Optional

from scfile import exceptions as exc
from scfile.source import McsaFile, MicFile, OlFile
from scfile.source.base import BaseSourceFile


def mcsa_to_obj(source: str, output: Optional[str] = None):
    """
    Converting `.mcsa` file to `.obj`.

    Args:
        source: Full path to `.mcsa` file.
        output (optional): Full path to output `.obj` file.
        Defaults to source path with new suffix.

    Example:
        `mcsa_to_obj("C:/file.mcsa", "C:/file.obj")`
    """

    _convert(source, output, McsaFile, ".obj")


def mic_to_png(source: str, output: Optional[str] = None):
    """
    Converting `.mic` file to `.png`.

    Args:
        source: Full path to `.mic` file.
        output (optional): Full path to output `.png` file.
        Defaults to source path with new suffix.

    Example:
        `mic_to_png("C:/file.mic", "C:/file.png")`
    """

    _convert(source, output, MicFile, ".png")


def ol_to_dds(source: str, output: Optional[str] = None):
    """
    Converting `.ol` file to `.dds`.

    Args:
        source: Full path to `.ol` file.
        output (optional): Full path to output `.dds` file.
        Defaults to source path with new suffix.

    Example:
        `ol_to_dds("C:/file.ol", "C:/file.dds")`
    """

    _convert(source, output, OlFile, ".dds")


def auto(source: str, output: Optional[str] = None):
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
        case ".mic":
            mic_to_png(source, output)

        case ".ol":
            ol_to_dds(source, output)

        case ".mcsa":
            mcsa_to_obj(source, output)

        case _:
            raise exc.UnsupportedFormat(f"File '{source_path.as_posix()}' is unsupported.")


def _convert(
    source: str,
    output: Optional[str],
    converter: type[BaseSourceFile],
    suffix: str
):
    src = Path(source)
    dest = Path(output) if output else src.with_suffix(suffix)

    if not src.exists() or not src.is_file():
        raise exc.SourceFileNotFound(f"File '{src.as_posix()}' not found.")

    with open(src, "rb") as f:
        converted = converter(f).convert()

    with open(dest, "wb") as f:
        f.write(converted)
