import click

from .callbacks import updates_callback, version_callback
from .cmd.animate import animate
from .cmd.convert import convert
from .cmd.mapcache import mapcache
from .cmd.mapmerge import mapmerge
from .routing import resolve


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
def scfile() -> None: ...


scfile.add_command(animate)
scfile.add_command(convert)
scfile.add_command(mapcache)
scfile.add_command(mapmerge)


def run(
    args: list[str],
) -> int:
    result = scfile(args=resolve(args), standalone_mode=False)
    return result if isinstance(result, int) else 0
