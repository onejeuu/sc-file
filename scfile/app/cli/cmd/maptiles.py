from pathlib import Path

import click

from scfile.app.cli import params
from scfile.app.enums import CliCommand
from scfile.app.feedback import TaskFeedback
from scfile.app.game import GameRegion, GameRoot
from scfile.app.localization import system_language
from scfile.app.tasks import execute
from scfile.app.tasks.maptiles import MapTilesImage, MapTilesTask
from scfile.convert import maptiles as maps
from scfile.options import Options


@click.command(name=CliCommand.MAPTILES)
@click.argument("SOURCE", type=params.MapTilesDir)
@click.argument("TARGET")
@click.argument("OUTPUT", type=params.MapTilesOutput, required=False)
@click.option("--region", metavar="REGION", help="Game region for localized map assets.")
@click.option("--jpeg-quality", type=click.IntRange(0, 100), help="JPEG quality.")
@click.option("--png-compression", type=click.IntRange(0, 9), help="PNG compression level.")
def maptiles(
    source: Path,
    target: str,
    output: Path | None,
    region: str | None,
    jpeg_quality: int | None,
    png_compression: int | None,
) -> None:
    """Assemble 2D map tiles."""

    task = _task(source, target, output, region, jpeg_quality, png_compression)

    feedback = TaskFeedback()
    summary = execute(task, feedback)
    feedback.finish(summary)

    if summary.work.failed:
        raise click.exceptions.Exit(1)


def _task(
    source: Path,
    target: str,
    output: Path | None,
    region: str | None,
    jpeg_quality: int | None,
    png_compression: int | None,
) -> MapTilesTask:
    if output is None:
        output = Path(target).expanduser().resolve()
        if output.is_dir():
            raise click.BadParameter("Output must be a file path.", param_hint="OUTPUT")
        tiles = _flat(source, region)
    else:
        tiles = _game(source, target, region)

    save = _save(output, jpeg_quality, png_compression)
    return MapTilesTask(tiles, output, Options(), save)


def _flat(source: Path, region: str | None) -> maps.Tiles:
    if region is not None:
        raise click.UsageError("--region requires a game folder and map name.")

    tiles = maps.scan(source)
    if not tiles:
        raise click.BadParameter("No map tiles found.", param_hint="SOURCE")

    return tiles


def _game(source: Path, name: str, region: str | None) -> maps.Tiles:
    game = GameRoot.find(source)
    if game is None:
        raise click.BadParameter("Specify a STALCRAFT game folder.", param_hint="SOURCE")

    if Path(name).name != name:
        raise click.BadParameter("Map name must not contain a path.", param_hint="TARGET")

    selected = _region(game, region)
    tiles = maps.collect(game.asset_paths(Path("pda") / name, selected))
    if not tiles:
        raise click.BadParameter(f"No map tiles found for '{name}'.", param_hint="TARGET")

    return tiles


def _save(
    output: Path,
    jpeg_quality: int | None,
    png_compression: int | None,
) -> maps.SaveOptions:
    image_format = MapTilesImage.parse(output)
    if image_format is None:
        raise click.BadParameter("Output extension must be .jpg, .jpeg, or .png.", param_hint="OUTPUT")

    match image_format:
        case MapTilesImage.JPEG:
            if png_compression is not None:
                raise click.BadParameter(
                    "--png-compression requires PNG output.",
                    param_hint="--png-compression",
                )
            return image_format.save(jpeg_quality)
        case MapTilesImage.PNG:
            if jpeg_quality is not None:
                raise click.BadParameter(
                    "--jpeg-quality requires JPEG output.",
                    param_hint="--jpeg-quality",
                )
            return image_format.save(png_compression)


def _region(game: GameRoot, value: str | None) -> GameRegion:
    regions = game.regions
    if value is None:
        preferred = GameRegion(system_language().lower())
        return preferred if preferred in regions or not regions else regions[0]

    if value not in regions:
        choices = ", ".join(regions) or "none"
        raise click.BadParameter(f"Unknown region '{value}' (available: {choices}).", param_hint="--region")

    return GameRegion(value)
