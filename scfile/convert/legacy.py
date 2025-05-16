"""
Implement functions to convert legacy mcsa format to another by simplest way.
"""

from typing import Optional

from scfile.core.context import UserOptions
from scfile.core.types import PathLike
from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder

from .formats import converter


@converter(McsaDecoder, DaeEncoder)
def mcsa_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsa` to `.dae` format.

    Arguments:
        source: Path to input `.mcsa` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): Model conversion settings. Default: `None`.
        overwrite (optional): Overwrite files with same name. Defaults: `True`.

    Example:
        `mcsa_to_dae("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsaDecoder, ObjEncoder)
def mcsa_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsa` to `.obj` format.

    Arguments:
        source: Path to input `.mcsa` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): Model conversion settings. Default: `None`.
        overwrite (optional): Overwrite files with same name. Defaults: `True`.

    Example:
        `mcsa_to_obj("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsaDecoder, GlbEncoder)
def mcsa_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsa` to `.glb` (gltf) format.

    Arguments:
        source: Path to input `.mcsa` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): Model conversion settings. Default: `None`.
        overwrite (optional): Overwrite files with same name. Defaults: `True`.

    Example:
        `mcsa_to_gltf("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(McsaDecoder, Ms3dEncoder)
def mcsa_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsa` to `.ms3d` format.

    Arguments:
        source: Path to input `.mcsa` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): Model conversion settings. Default: `None`.
        overwrite (optional): Overwrite files with same name. Defaults: `True`.

    Example:
        `mcsa_to_ms3d("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """
