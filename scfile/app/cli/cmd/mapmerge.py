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
    """Merge 2D map tiles."""

    if output is None:
        task = _flat(source, target, region)
    else:
        task = _game(source, target, output, region)

    if task.output.exists():
        warn(f"Output file will be replaced: {task.output}")

    feedback = TaskFeedback()
    summary = execute(task, feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)


def _flat(source: Path, output: str, region: str | None) -> MapMergeTask:
    if region is not None:
        raise click.UsageError("--region requires a game folder and map name.")

    path = Path(output).expanduser().resolve()
    if path.is_dir():
        raise click.BadParameter("Output must be a file path.", param_hint="OUTPUT")

    tiles = maps.scan(source)
    if not tiles:
        raise click.BadParameter("No map tiles found.", param_hint="SOURCE")

    return MapMergeTask(tiles, path, Options())


def _game(source: Path, name: str, output: Path, region: str | None) -> MapMergeTask:
    game = GameRoot.find(source)
    if game is None:
        raise click.BadParameter("Specify a STALCRAFT game folder.", param_hint="SOURCE")

    if Path(name).name != name:
        raise click.BadParameter("Map name must not contain a path.", param_hint="TARGET")

    selected = _region(game, region)
    tiles = maps.collect(game.asset_paths(Path("pda") / name, selected))
    if not tiles:
        raise click.BadParameter(f"No map tiles found for '{name}'.", param_hint="TARGET")

    return MapMergeTask(tiles, output, Options())


def _region(game: GameRoot, value: str | None) -> GameRegion:
    regions = game.regions
    if value is None:
        preferred = GameRegion(system_language().lower())
        return preferred if preferred in regions or not regions else regions[0]

    if value not in regions:
        choices = ", ".join(regions) or "none"
        raise click.BadParameter(f"Unknown region '{value}' (available: {choices}).", param_hint="--region")

    return GameRegion(value)
