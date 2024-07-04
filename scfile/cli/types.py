import pathlib

import click

from scfile.consts import OutputFormats


PATH_TYPE = pathlib.Path

FILES = click.Path(path_type=PATH_TYPE, dir_okay=True, file_okay=True, exists=True, resolve_path=True)
OUTPUT = click.Path(path_type=PATH_TYPE, dir_okay=True, file_okay=False)
FORMATS = click.Choice(list(OutputFormats.MODELS))
