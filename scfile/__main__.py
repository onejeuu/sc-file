import sys

import click
from rich import print

from scfile.cli.cmd import scfile
from scfile.enums import CliCommand, L


def setup_command():
    user_args = sys.argv[1:]

    # Run GUI if no arguments are provided
    if not user_args:
        from scfile.gui import window

        return window.run()

    # Show default help
    if "--help" in user_args:
        return

    # Backfill command if missing
    if command := _default_command(user_args):
        sys.argv.insert(1, command)


def _default_command(args: list[str]):
    first_arg = args[0]

    # Map cache override
    if "map_cache" in first_arg:
        return CliCommand.MAPCACHE

    # Use existing command if valid
    if first_arg in scfile.commands:
        return None

    return CliCommand.CONVERT  # Fallback


def main():
    """Program entrypoint."""

    try:
        setup_command()
        scfile(standalone_mode=False)

    except click.ClickException as err:
        print(L.INVALID, str(err))

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[yellow]Operation aborted.[/]")

    sys.exit()


if __name__ == "__main__":
    main()
