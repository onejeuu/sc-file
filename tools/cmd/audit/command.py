from pathlib import Path

import click
from rich.console import Console

from tools.cmd import tools

from . import config, relations
from .audit import Audit


@tools.command()
@click.argument(
    "PATH",
    required=False,
    type=click.Path(path_type=Path, file_okay=False),
)
@click.option(
    "-F",
    "--formats",
    type=click.Choice(config.FORMATS, case_sensitive=False),
    multiple=True,
    help="Formats to check. Repeat for multiple formats.",
)
@click.option(
    "-R",
    "--relations",
    type=click.Choice(relations.NAMES, case_sensitive=False),
    multiple=True,
    help="Relations to check. Repeat for multiple relations.",
)
@click.option(
    "-W",
    "--workers",
    type=click.IntRange(min=0),
    help="Worker threads.",
)
@click.option(
    "--animation",
    is_flag=True,
    default=None,
    help="Parse model skeletons and animations.",
)
@click.option(
    "--stats",
    is_flag=True,
    default=None,
    help="Write statistics.",
)
def audit(
    path: Path | None,
    formats: tuple[str, ...],
    relations: tuple[str, ...],
    workers: int | None,
    animation: bool | None,
    stats: bool | None,
) -> None:
    settings = config.resolve(path, formats, relations, workers, animation, stats)
    raise SystemExit(Audit(settings, Console()).run())
