import sys
import traceback
from typing import Never

import click
from rich import print
from rich.markup import escape

from scfile.app.cli import routing
from scfile.app.cli.cmd import scfile
from scfile.enums import L


def _run_gui() -> None:  # pragma: no cover
    try:
        from scfile.app.gui import window

        window.run()

    except ImportError:
        print(traceback.format_exc())
        print(f"{L.ERROR} GUI is not available")
        print(f"{L.INFO} Try install with: pip install {escape('sc-file[gui]')} -U")
        print(f"{L.INFO} Or in local environment: uv sync --extra gui")
        print()
        print(f"{L.HINT} If your system does not support graphical interfaces, use command line: scfile --help")
        input("\nPress Enter to exit...")
        sys.exit(1)


def _ensure_command() -> None:
    args = sys.argv[1:]

    # Run GUI if no arguments
    if not args:
        _run_gui()
        return

    # Allow default commands
    if set(("--help", "--version", "--updates")) & set(args):
        return

    # Backfill command if missing
    if command := _default_command(args):
        sys.argv[1:1] = command


def _default_command(args: list[str]) -> list[str] | None:
    first_arg = args[0]

    # Use explicit command
    if first_arg in scfile.commands:
        return None

    return routing.resolve(args)


def main() -> Never:
    """Program entrypoint."""

    try:
        _ensure_command()
        scfile(standalone_mode=False)

    except click.ClickException as err:
        print(L.INVALID, str(err))

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[yellow]Operation aborted.[/]")

    sys.exit()


if __name__ == "__main__":  # pragma: no cover
    main()
