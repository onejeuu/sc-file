from pathlib import Path
from typing import Optional

import click
from rich import print

from scfile.exceptions import ScFileException
from scfile.utils import convert


def convert_file(src: Path, dest: Optional[Path] = None):
    try:
        convert.auto(src, dest)

    except ScFileException as err:
        print(f"\n[b red]Error:[/] {err}")

    except Exception as err:
        print(f"\n[b red]Unknown Error:[/] '{src}' - {err}")

def convert_files(files: tuple[Path], dest: Optional[Path] = None):
    for src in files:
        convert_file(src, dest)

@click.command(no_args_is_help=True)
@click.argument(
    "files",
    type=click.Path(path_type=Path, exists=True, readable=True, dir_okay=False),
    nargs=-1
)
@click.option(
    "-O", "--output",
    help="Optional path to output. Defaults to source path with new suffix.",
    type=click.Path(path_type=Path, exists=False, writable=True, dir_okay=True),
    multiple=True,
    nargs=1,
)
def main(files: tuple[Path], output: Optional[tuple[Path]] = None):
    if not output:
        convert_files(files)
        return

    first_output = output[0]
    if first_output.is_dir():
        convert_files(files, first_output)
        return

    for src, dest in zip(files, output):
        convert_file(src, dest)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\n[b yellow]Operation aborted.[/]")
