import click
from rich import print

from scfile import convert, exceptions, types
from scfile.cli import params
from scfile.enums import CliCommand, L

from . import scfile


@scfile.command(name=CliCommand.ANIMATE)
@click.argument(
    "ANIMATION",
    type=params.File,
)
@click.argument(
    "MODELS",
    nargs=-1,
    required=True,
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=True,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def animate_command(
    animation: types.Path,
    models: tuple[types.Path, ...],
    output: types.Output,
) -> None:
    """Apply MCVD animations to MCSB models."""

    try:
        convert.animate(
            animation,
            *models,
            output=output,
        )
        print(L.DONE, f"'{animation}'")

    except exceptions.ScFileException as err:
        raise click.ClickException(str(err)) from None
