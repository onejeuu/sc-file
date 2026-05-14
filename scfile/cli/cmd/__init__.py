import click

from scfile.utils import versions


@click.group()
@click.option(
    "--version",
    help="Show the version and exit.",
    callback=versions.callback,
    is_flag=True,
    is_eager=True,
    expose_value=False,
)
def scfile():
    pass
