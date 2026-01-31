"""
Implement functions to convert one format to another by simplest way.
"""

from typing import Optional

from scfile import formats
from scfile.core import UserOptions
from scfile.types import PathLike

from .factory import converter


@converter(formats.mcsb.McsbDecoder, formats.obj.ObjEncoder)
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


@converter(formats.mcsb.McsbDecoder, formats.glb.GlbEncoder)
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


@converter(formats.mcsb.McsbDecoder, formats.dae.DaeEncoder)
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


@converter(formats.mcsb.McsbDecoder, formats.ms3d.Ms3dEncoder)
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


@converter(formats.ol.OlDecoder, formats.dds.DdsEncoder)
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


@converter(formats.hdri.OlCubemapDecoder, formats.dds.DdsEncoder)
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


@converter(formats.mic.MicDecoder, formats.png.PngEncoder)
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


@converter(formats.texarr.TextureArrayDecoder, formats.zip.TextureArrayEncoder)
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


@converter(formats.nbt.NbtDecoder, formats.json.JsonEncoder)
def nbt_to_json(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts data from `NBT` to `.json` format.

    Arguments:
        source: Path to input `NBT` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `nbt_to_json("itemnames.dat", "path/to/output")`
    """
