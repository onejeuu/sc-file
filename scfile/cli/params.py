"""
Click parameter types for commands.
"""

import click

from scfile import types
from scfile.options import ON_CONFLICT_OPTIONS
from scfile.enums import FileFormat


Files = click.Path(
    path_type=types.Path,
    dir_okay=True,
    file_okay=True,
    exists=True,
    resolve_path=True,
)

File = click.Path(
    path_type=types.Path,
    dir_okay=False,
    file_okay=True,
    exists=True,
    resolve_path=True,
)

OutputPath = click.Path(
    path_type=types.Path,
    dir_okay=True,
    file_okay=True,
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


MODEL_FORMAT_ORDER = (
    FileFormat.OBJ,
    FileFormat.GLB,
    FileFormat.FBX,
    FileFormat.DAE,
    FileFormat.MS3D,
)

Formats = click.Choice(
    choices=list(MODEL_FORMAT_ORDER),
    case_sensitive=False,
)

OnConflict = click.Choice(
    choices=ON_CONFLICT_OPTIONS,
    case_sensitive=False,
)
