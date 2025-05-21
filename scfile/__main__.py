import sys

import click
from rich import print

from scfile.cli import scfile
from scfile.cli.enums import Prefix


def main():
    """Program entrypoint."""

    try:
        scfile(standalone_mode=False)

    except click.ClickException as err:
        print(Prefix.INVALID, str(err))

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[yellow]Operation aborted.[/]")

    sys.exit(1)


if __name__ == "__main__":
    main()
