from pathlib import Path
from typing import Optional

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


def convert_multiple_files(files: tuple[Path], dest: Optional[Path] = None):
    for src in files:
        convert_file(src, dest)
