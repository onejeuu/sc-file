"""
Implement functions to convert one format to another by simplest way.
"""

from typing import Optional

from scfile.core.context import UserOptions
from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.hdri.decoder import OlCubemapDecoder
from scfile.formats.mcsb.decoder import McsbDecoder
from scfile.formats.mic.decoder import MicDecoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder
from scfile.formats.ol.decoder import OlDecoder
from scfile.formats.png.encoder import PngEncoder
from scfile.formats.texarr.decoder import TextureArrayDecoder
from scfile.formats.zip.encoder import TextureArrayEncoder
from scfile.types import PathLike

from .factory import converter


@converter(McsbDecoder, DaeEncoder)
def mcsb_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsb` to `.dae` format.

    Arguments:
        source: Path to input `.mcsb` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mcsb_to_dae("model.mcsb", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsbDecoder, ObjEncoder)
def mcsb_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsb` to `.obj` format.

    Arguments:
        source: Path to input `.mcsb` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mcsb_to_obj("model.mcsb", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsbDecoder, GlbEncoder)
def mcsb_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsb` to `.glb` format.

    Arguments:
        source: Path to input `.mcsb` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mcsb_to_glb("model.mcsb", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsbDecoder, Ms3dEncoder)
def mcsb_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsb` to `.ms3d` format.

    Arguments:
        source: Path to input `.mcsb` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mcsb_to_ms3d("model.mcsb", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(OlDecoder, DdsEncoder)
def ol_to_dds(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts texture from `.ol` to `.dds` format.

    Arguments:
        source: Path to input `.ol` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `ol_to_dds("texture.ol", "path/to/output")`
    """


@converter(OlCubemapDecoder, DdsEncoder)
def ol_cubemap_to_dds(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts cubemap texture from `.ol` to `.dds` format.

    Arguments:
        source: Path to input `.ol` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `ol_cubemap_to_dds("cubemap.ol", "path/to/output")`
    """


@converter(MicDecoder, PngEncoder)
def mic_to_png(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts image from `.mic` to `.png` format.

    Arguments:
        source: Path to input `.mic` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mic_to_png("image.mic", "path/to/output")`
    """


@converter(TextureArrayDecoder, TextureArrayEncoder)
def texarr_to_zip(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts archive from `.texarr` to `.zip` format.

    Arguments:
        source: Path to input `.texarr` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `texarr_to_zip("blockMap.texarr", "path/to/output")`
    """
