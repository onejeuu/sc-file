__version__ = "6.0.0"
__author__ = "onejeuu"
__license__ = "MIT"

__repository__ = "onejeuu/sc-file"

from .core import Options
from . import consts, enums, exceptions, structures, types
from . import formats, operations, registry, convert, cli


__all__ = (
    "Options",
    "cli",
    "convert",
    "core",
    "exceptions",
    "formats",
    "operations",
    "registry",
    "structures",
    "consts",
    "enums",
    "types",
)
