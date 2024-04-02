from pathlib import Path
from typing import Optional

import click
from rich import print

from scfile.cli.consts import Types
from scfile.cli.convert import convert_file, convert_files


@click.command(no_args_is_help=True)
@click.argument(
    "files",
    type=Types.FILES,
    nargs=-1,
)
@click.option(
    "-O",
    "--output",
    help="Optional path to output. Defaults to source path with new suffix.",
    type=Types.OUTPUT,
    multiple=True,
    nargs=1,
)
def convert_auto(files: tuple[Path], output: Optional[tuple[Path]] = None):
    if not output:
        convert_files(files)
        return

    first_output = output[0]
    if first_output.is_dir():
        convert_files(files, first_output)
        return

    for src, dest in zip(files, output):
        convert_file(src, dest)


def main():
    try:
        convert_auto()

    except KeyboardInterrupt:
        print("\n\n[b yellow]Operation aborted.[/]")
