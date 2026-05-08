import sys
from typing import Never

import click
from rich import print

from scfile.cli.cmd import scfile
from scfile.enums import CliCommand, L


def ensure_command() -> None:
    args = sys.argv[1:]

    # Run GUI if no arguments
    if not args:
        from scfile.gui import window

        return window.run()

    # Show default help
    if "--help" in args:
        return

    # Backfill command if missing
    if command := _default_command(args):
        sys.argv.insert(1, command)


def _default_command(args: list[str]) -> CliCommand | None:
    first_arg = args[0]

    # Use explicit command
    if first_arg in scfile.commands:
        return None

    # Use map cache if path detected
    if "map_cache" in first_arg:
        return CliCommand.MAPCACHE

    return CliCommand.CONVERT  # Fallback


def main() -> Never:
    """Program entrypoint."""

    try:
        ensure_command()
        scfile(standalone_mode=False)

    except click.ClickException as err:
        print(L.INVALID, str(err))

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[yellow]Operation aborted.[/]")

    sys.exit()


if __name__ == "__main__":
    main()
