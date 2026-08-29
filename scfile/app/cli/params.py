from pathlib import Path

import click

from scfile.app.enums import OutputLayout
from scfile.app.formats import model_formats
from scfile.enums import OnConflict
from scfile.formats import registry


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

MapMergeDir = click.Path(
    path_type=Path,
    dir_okay=True,
    file_okay=False,
    exists=True,
    resolve_path=True,
)

MapMergeOutput = click.Path(
    path_type=Path,
    dir_okay=False,
    file_okay=True,
    resolve_path=True,
)

ModelFormats = click.Choice(
    choices=model_formats(),
    case_sensitive=False,
)

InputFormats = click.Choice(
    choices=sorted(registry.decoders),
    case_sensitive=False,
)

Layouts = click.Choice(
    choices=list(OutputLayout),
    case_sensitive=False,
)

Conflicts = click.Choice(
    choices=list(OnConflict),
    case_sensitive=False,
)
