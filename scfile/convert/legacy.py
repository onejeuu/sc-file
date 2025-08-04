"""
Implement functions to convert legacy mcsa format to another by simplest way.
"""

from typing import Optional

from scfile import formats
from scfile.core import UserOptions
from scfile.types import PathLike

from .formats import converter


@converter(formats.mcsa.McsaDecoder, formats.obj.ObjEncoder)
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
        options (optional): User settings. Default: `None`.

    Example:
        `mcsa_to_obj("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(formats.mcsa.McsaDecoder, formats.glb.GlbEncoder)
def mcsa_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
):
    """
    Converts model from `.mcsa` to `.glb` format.

    Arguments:
        source: Path to input `.mcsa` file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `mcsa_to_glb("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(formats.mcsa.McsaDecoder, formats.dae.DaeEncoder)
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
        options (optional): User settings. Default: `None`.

    Example:
        `mcsa_to_dae("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """


@converter(formats.mcsa.McsaDecoder, formats.ms3d.Ms3dEncoder)
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
        options (optional): User settings. Default: `None`.

    Example:
        `mcsa_to_ms3d("model.mcsa", "path/to/output", UserOptions(parse_skeleton=True))`
    """
