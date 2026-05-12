"""
Data types for CLI wrapper.
"""

import click

from scfile import types
from scfile.consts import OutputFormats


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

RetargetPath = click.Path(
    path_type=types.Path,
    dir_okay=False,
    file_okay=True,
    exists=True,
    resolve_path=True,
)

Formats = click.Choice(
    choices=list(OutputFormats.MODELS),
    case_sensitive=False,
)
