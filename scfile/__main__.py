import sys
import traceback
from typing import Never

import click

from scfile.app.cli import console, routing
from scfile.app.cli.cmd import scfile


def _run_gui() -> None:  # pragma: no cover
    try:
        from scfile.app.gui import window

        window.run()

    except ImportError:
        console.CONSOLE.print(traceback.format_exc(), markup=False, highlight=False)
        console.error("GUI is not available")
        console.info("Try install with: pip install sc-file[gui] -U")
        console.info("Or in local environment: uv sync --extra gui")
        console.CONSOLE.print()
        console.hint("If your system does not support graphical interfaces, use command line: scfile --help")
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

    status = 0
    try:
        _ensure_command()
        result = scfile(standalone_mode=False)
        if isinstance(result, int):
            status = result

    except click.ClickException as error:
        console.invalid(str(error))
        status = error.exit_code

    except (KeyboardInterrupt, click.exceptions.Abort):
        console.aborted("Operation aborted.")
        status = 130

    sys.exit(status)


if __name__ == "__main__":  # pragma: no cover
    main()
