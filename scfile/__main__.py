import sys
from pathlib import Path

import click
from rich import print

from scfile.cli.cmd import scfile
from scfile.enums import CliCommand, L


def normalize():
    args = sys.argv[1:]

    default_command = CliCommand.CONVERT

    if args and Path(args[0]).as_posix().endswith("map_cache/5.0"):
        default_command = CliCommand.MAPCACHE

    elif not args or args[0] not in scfile.commands.keys():
        default_command = CliCommand.CONVERT

    else:
        default_command = None

    if default_command:
        sys.argv.insert(1, default_command)


def main():
    """Program entrypoint."""

    normalize()

    try:
        scfile(standalone_mode=False)

    except click.ClickException as err:
        print(L.INVALID, str(err))

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[yellow]Operation aborted.[/]")

    sys.exit()


if __name__ == "__main__":
    main()
