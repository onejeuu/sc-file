from pathlib import Path

import click

from scfile.app.enums import OutputLayout
from scfile.app.formats import model_formats
from scfile.options import ON_CONFLICT_OPTIONS
from scfile.registry import REGISTRY


Files = click.Path(
    path_type=Path,
    dir_okay=True,
    file_okay=True,
    resolve_path=True,
)

SourceFile = click.Path(
    path_type=Path,
    dir_okay=False,
    file_okay=True,
    exists=True,
    resolve_path=True,
)

OutputPath = click.Path(
    path_type=Path,
    dir_okay=True,
    file_okay=True,
    resolve_path=True,
)

OutputDir = click.Path(
    path_type=Path,
    dir_okay=True,
    file_okay=False,
    resolve_path=True,
)

MapCacheDir = click.Path(
    path_type=Path,
    dir_okay=True,
    file_okay=False,
    exists=True,
    resolve_path=True,
)

ModelFormats = click.Choice(
    choices=model_formats(),
    case_sensitive=False,
)

InputFormats = click.Choice(
    choices=sorted(REGISTRY.supported_formats),
    case_sensitive=False,
)

Layouts = click.Choice(
    choices=list(OutputLayout),
    case_sensitive=False,
)

OnConflict = click.Choice(
    choices=ON_CONFLICT_OPTIONS,
    case_sensitive=False,
)
