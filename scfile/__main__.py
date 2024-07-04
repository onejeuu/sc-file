import click
from rich import print

from scfile.cli.scfile import scfile


def main():
    try:
        scfile(standalone_mode=False)

    except (KeyboardInterrupt, click.exceptions.Abort):
        print("[b yellow]Operation Aborted.[/]")


if __name__ == "__main__":
    main()
