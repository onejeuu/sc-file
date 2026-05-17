__version__ = "5.0.0-dev"
__author__ = "onejeuu"
__license__ = "MIT"

__repository__ = "onejeuu/sc-file"

from . import cli, consts, convert, core, enums, exceptions, formats, structures
from .core import UserOptions


__all__ = (
    "cli",
    "convert",
    "core",
    "exceptions",
    "formats",
    "structures",
    "consts",
    "enums",
    "UserOptions",
)
