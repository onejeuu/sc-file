from pathlib import Path
from typing import Optional

import click
from rich import print

from .consts import Types
from .convert import convert_multiple_files


@click.command(no_args_is_help=True)
@click.argument("files", type=Types.FILES, nargs=-1)
@click.option(
    "-O",
    "--output",
    help="Optional path to output directory.",
    type=Types.OUTPUT,
    multiple=False,
    nargs=1,
)
def default(files: tuple[Path], output: Optional[Path] = None):
    convert_multiple_files(files, output)


def main():
    try:
        default()

    except KeyboardInterrupt:
        print("\n\n[b yellow]Operation aborted.[/]")
