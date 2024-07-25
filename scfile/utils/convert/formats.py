from typing import Optional

from scfile.file.base.decoder import DATA, OPENER, FileDecoder
from scfile.file.base.encoder import FileEncoder
from scfile.file.formats.dae import DaeEncoder
from scfile.file.formats.dds import DdsEncoder
from scfile.file.formats.mcsa import McsaDecoder
from scfile.file.formats.mic import MicDecoder
from scfile.file.formats.ms3d import Ms3dBinEncoder
from scfile.file.formats.ms3d_ascii import Ms3dAsciiEncoder
from scfile.file.formats.obj import ObjEncoder
from scfile.file.formats.ol import OlDecoder
from scfile.file.formats.ol.decoder import OlHdriDecoder
from scfile.file.formats.png import PngEncoder
from scfile.utils.types import PathLike

from .convert import convert


def converter(decoder: type[FileDecoder[OPENER, DATA]], encoder: type[FileEncoder[DATA]]):
    def decorator(_):
        def wrapper(source: PathLike, output: Optional[PathLike] = None, overwrite: bool = True):
            convert(source, output, decoder, encoder, overwrite)

        return wrapper

    return decorator


@converter(McsaDecoder, DaeEncoder)
def mcsa_to_dae(*args, **kwargs):
    """
    Converting model `.mcsa` file to `.dae`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `mcsa_to_dae("model.mcsa", "path/to/output")`
    """


@converter(McsaDecoder, ObjEncoder)
def mcsa_to_obj(*args, **kwargs):
    """
    Converting model `.mcsa` file to `.obj`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `mcsa_to_obj("model.mcsa", "path/to/output")`
    """


@converter(McsaDecoder, Ms3dBinEncoder)
def mcsa_to_ms3d(*args, **kwargs):
    """
    Converting model `.mcsa` file to `.ms3d`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `mcsa_to_ms3d("model.mcsa", "path/to/output")`
    """


@converter(McsaDecoder, Ms3dAsciiEncoder)
def mcsa_to_ms3d_ascii(*args, **kwargs):
    """
    Converting model `.mcsa` file to `.txt`.

    Args:
        source: Path to `.mcsa` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `mcsa_to_ms3d_ascii("model.mcsa", "path/to/output")`
    """


@converter(MicDecoder, PngEncoder)
def mic_to_png(*args, **kwargs):
    """
    Converting image `.mic` file to `.png`.

    Args:
        source: Path to `.mic` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `mic_to_png("image.mic", "path/to/output")`
    """


@converter(OlDecoder, DdsEncoder)
def ol_to_dds(*args, **kwargs):
    """
    Converting texture `.ol` file to `.dds`.

    Args:
        source: Path to `.ol` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `ol_to_dds("texture.ol", "path/to/output")`
    """


@converter(OlHdriDecoder, DdsEncoder)
def ol_hdri_to_dds(*args, **kwargs):
    """
    Converting hdri (sky) texture `.ol` file to `.dds`.

    Args:
        source: Path to `.ol` file.
        output (optional): Path to output directory. Defaults to source path with new suffix.
        overwrite (optional): Whether to overwrite output file if already exists. Defaults to True.

    Example:
        `ol_to_dds("texture.ol", "path/to/output")`
    """
