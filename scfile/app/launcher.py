import sys
from typing import Never

import click
from rich.text import Text

from .cli import console
from .cli import run as run_cli


def run_gui() -> int:  # pragma: no cover
    try:
        from .gui import application

        return application.run()

    except ImportError:
        console.error("GUI could not be loaded.")
        console.print(
            Text.assemble(
                "\nFor an installed package:\n",
                ('  pip install "sc-file[gui]" -U', "cyan"),
                "\n\nFor local development:\n",
                ("  uv sync --extra gui", "cyan"),
                "\n\nFor headless environments, use the command line:\n",
                ("  scfile --help", "cyan"),
            )
        )
        return 1


def main() -> Never:
    try:
        args = sys.argv[1:]
        if not args:
            status = run_gui()
        else:
            status = run_cli(args)

    except click.ClickException as error:
        console.invalid(str(error))
        status = error.exit_code

    except (KeyboardInterrupt, click.exceptions.Abort):
        console.aborted("Operation aborted.")
        status = 130

    sys.exit(status)
