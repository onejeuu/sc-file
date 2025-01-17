import click

from scfile.cli.scfile import scfile


def main():
    try:
        scfile(standalone_mode=False)

    except (KeyboardInterrupt, click.exceptions.Abort):
        click.echo(click.style("Operation Aborted.", fg="yellow"))


if __name__ == "__main__":
    main()
