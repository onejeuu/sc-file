import click

from scfile.utils.cli import updates_callback, version_callback


@click.group()
@click.option(
    "--updates",
    help="Check for updates and exit.",
    callback=updates_callback,
    is_flag=True,
    is_eager=True,
    expose_value=False,
)
@click.option(
    "--version",
    help="Show the version and exit.",
    callback=version_callback,
    is_flag=True,
    is_eager=True,
    expose_value=False,
)
def scfile():
    pass
