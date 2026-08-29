from pathlib import Path

import click

from scfile.app.cli import params
from scfile.app.cli.console import warn
from scfile.app.enums import CliCommand
from scfile.app.feedback import TaskFeedback
from scfile.app.game import GameRegion, GameRoot
from scfile.app.localization import system_language
from scfile.app.tasks import execute
from scfile.app.tasks.mapmerge import MapMergeTask
from scfile.convert import mapmerge as maps
from scfile.options import Options


@click.command(name=CliCommand.MAPMERGE)
@click.argument("SOURCE", type=params.MapMergeDir)
@click.argument("TARGET")
@click.argument("OUTPUT", type=params.MapMergeOutput, required=False)
@click.option("--region", metavar="REGION", help="Game region for localized map assets.")
def mapmerge(source: Path, target: str, output: Path | None, region: str | None) -> None:
    """Merge map tiles into an image."""

    if output is None:
        if region is not None:
            raise click.UsageError("--region requires a game folder and map name.")

        output = Path(target).expanduser().resolve()
        if output.is_dir():
            raise click.BadParameter("Output must be a file path.", param_hint="OUTPUT")
        sources = (source,)

    else:
        game = GameRoot.find(source)
        if game is None:
            raise click.BadParameter("Specify a STALCRAFT game folder.", param_hint="SOURCE")

        if Path(target).name != target:
            raise click.BadParameter("Map name must not contain a path.", param_hint="TARGET")

        region = _region(game, region)
        sources = game.asset_paths(Path("pda") / target, region)
        if not maps.collect(sources):
            raise click.BadParameter(f"No map tiles found for '{target}'.", param_hint="TARGET")

    if output.exists():
        warn(f"Output file will be replaced: {output}")

    feedback = TaskFeedback()
    summary = execute(MapMergeTask(sources, output, Options()), feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)


def _region(game: GameRoot, value: str | None) -> GameRegion:
    regions = game.regions
    if value is None:
        preferred = GameRegion(system_language().lower())
        return preferred if preferred in regions or not regions else regions[0]

    if value not in regions:
        choices = ", ".join(regions) or "none"
        raise click.BadParameter(f"Unknown region '{value}' (available: {choices}).", param_hint="--region")

    return GameRegion(value)
