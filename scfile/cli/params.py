"""
Data types for CLI wrapper.
"""

import click

from scfile import types
from scfile.consts import OutputFormats
from scfile.core.options import ON_CONFLICT_OPTIONS


Files = click.Path(
    path_type=types.Path,
    dir_okay=True,
    file_okay=True,
    exists=True,
    resolve_path=True,
)

Output = click.Path(
    path_type=types.Path,
    dir_okay=True,
    file_okay=False,
    resolve_path=True,
)

MapCacheDir = click.Path(
    path_type=types.Path,
    dir_okay=True,
    file_okay=False,
    exists=True,
    resolve_path=True,
)


Formats = click.Choice(
    choices=list(OutputFormats.MODELS),
    case_sensitive=False,
)

OnConflict = click.Choice(
    choices=ON_CONFLICT_OPTIONS,
    case_sensitive=False,
)
