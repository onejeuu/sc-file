import pathlib

import click


class Types:
    FILES = click.Path(path_type=pathlib.Path, exists=True, readable=True, dir_okay=False)
    OUTPUT = click.Path(
        path_type=pathlib.Path, exists=True, writable=True, dir_okay=True, file_okay=False
    )
