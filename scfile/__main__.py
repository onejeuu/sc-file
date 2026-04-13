import sys
from pathlib import Path

import click
from rich import print

from scfile import gui
from scfile.cli.cmd import scfile
from scfile.enums import CliCommand, L


def setup_command():
    if len(sys.argv) == 1:
        gui.window.run()
        return

    args = sys.argv[1:]

    if "--help" in args:
        return

    default_command = CliCommand.CONVERT

    if args and "map_cache" in Path(args[0]).as_posix():
        default_command = CliCommand.MAPCACHE

    elif not args or args[0] not in scfile.commands.keys():
        default_command = CliCommand.CONVERT

    else:
        default_command = None

    if default_command:
        sys.argv.insert(1, default_command)


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
