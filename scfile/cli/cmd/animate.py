import click
from rich import print

from scfile import convert, exceptions, types
from scfile.cli import params
from scfile.enums import CliCommand, L

from . import scfile


@scfile.group(name=CliCommand.ANIMATE)
def animate() -> None:
    """Export models with external animations."""


@animate.command()
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
def arms(
    animation: types.Path,
    models: tuple[types.Path, ...],
    output: types.Output,
) -> None:
    """Apply first-person animation to weapon and hands models."""

    try:
        convert.animate(
            animation,
            *models,
            output=output,
        )
        print(L.DONE, f"'{animation}'")

    except exceptions.ScFileException as err:
        raise click.ClickException(str(err)) from None


@animate.command()
@click.argument(
    "ANIMATION",
    type=params.File,
)
@click.argument(
    "MODEL",
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=True,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def face(
    animation: types.Path,
    model: types.Path,
    output: types.Output,
) -> None:
    """Apply facial animation to a head model."""

    try:
        convert.lipsync(
            animation,
            model,
            output=output,
        )
        print(L.DONE, f"'{animation}'")

    except exceptions.ScFileException as err:
        raise click.ClickException(str(err)) from None


@animate.command()
@click.argument(
    "LIBRARY",
    type=params.File,
)
@click.argument(
    "MODEL",
    type=params.File,
)
@click.option(
    "-O",
    "--output",
    required=True,
    help="Output GLB file or directory.",
    type=params.OutputPath,
)
def body(
    library: types.Path,
    model: types.Path,
    output: types.Output,
) -> None:
    """Apply animation library to a model."""

    try:
        convert.apply_mcal(
            library,
            model,
            output=output,
        )
        print(L.DONE, f"'{library}'")

    except exceptions.ScFileException as err:
        raise click.ClickException(str(err)) from None
