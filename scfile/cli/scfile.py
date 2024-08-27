import sys
from pathlib import Path
from typing import Optional, Sequence

import click
from rich import print

from scfile.cli.excepthook import excepthook
from scfile.consts import CLI
from scfile.enums import EchoPrefix as PREFIX
from scfile.enums import FileSuffix
from scfile.exceptions import ScFileException
from scfile.utils import convert

from . import types


sys.excepthook = excepthook


@click.command(no_args_is_help=True, epilog=CLI.EPILOG)
@click.argument("FILES", type=types.FILES, nargs=-1, required=True)
@click.option("-F", "--formats", help="Preferred format for models.", multiple=True, type=types.FORMATS)
@click.option("-O", "--output", type=types.OUTPUT, help="Output results directory.")
@click.option("--subdir", is_flag=True, help="Recreate input subdirectories to output.")
@click.option("--hdri", is_flag=True, help="All ol textures in input files is hdri (skies).")
@click.option("--no-overwrite", is_flag=True, help="Do not overwrite file if already exists.")
@click.option("--silent", is_flag=True, help="Suppress all console echoes.")
def scfile(
    files: Sequence[Path],
    formats: Sequence[FileSuffix],
    output: Optional[Path] = None,
    subdir: bool = False,
    hdri: bool = False,
    no_overwrite: bool = False,
    silent: bool = False,
):
    # TODO: pretty click error handler and echo
    def echo(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)

    # Reverse overwrite flag
    overwrite = not no_overwrite

    # Title echo
    echo(f"[b purple]SCFILE:[/] {CLI.VERSION}")
    echo()

    # Warn invalid flags
    if subdir and not output:
        echo(PREFIX.WARN, "[b]--subdir[/] flag cannot be used without specifying [b]--output[/] option.")
        echo()

    # Get root path for --subdir output
    first_path = files[0]
    root = first_path if first_path.is_dir() else None

    # Create glob from directory input
    if first_path.is_dir():
        # haven't figured out how to implement
        # multiple directories with --output and --recusive support
        if len(files) != 1:
            echo(PREFIX.ERROR, "Only one directory suported at once.")
            return

        files = tuple(first_path.rglob("**/*"))

    # Exclude directories and unsupported files
    files = tuple(filter(lambda path: path.is_file() and convert.is_supported(path), files))

    # Check that files not empty
    if not files:
        echo(PREFIX.ERROR, "No supported files found in provided arguments.")
        echo(PREFIX.INFO, CLI.FORMATS)
        return

    # Convert all files
    for source in files:
        destination = output

        # Get relative destination path
        if output and subdir and root:
            relative = source.parent.relative_to(root)
            destination = Path(output or "") / relative

        # Convert source file
        try:
            convert.auto(source, destination, formats, overwrite, hdri)
            echo(PREFIX.INFO, f"File '{source.name}' converted to '{destination or source.parent}'.")

        except ScFileException as err:
            echo(PREFIX.ERROR, str(err))

        except Exception as err:
            echo(PREFIX.EXCEPTION, f"'{source}' - {err}")
