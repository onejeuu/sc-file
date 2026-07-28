import json
import time
from collections import Counter
from contextlib import nullcontext
from itertools import chain
from pathlib import Path

import click
from rich.console import Console, Group
from rich.live import Live
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from tools.cmd import tools

from . import files, relations, stats
from .config import Config
from .consts import ERRORS_JSONL, FILES, FORMATS
from .types import Error


def table(found: Counter, checked: Counter, failed: Counter) -> Table:
    output = Table()
    output.add_column("Format", style="cyan")
    output.add_column("Files", justify="right")
    output.add_column("Checked", justify="right", style="green")
    output.add_column("Errors", justify="right", style="red")

    for format in sorted(found):
        output.add_row(format, str(found[format]), str(checked[format]), str(failed[format]))

    output.add_section()
    output.add_row("Total", str(found.total()), str(checked.total()), str(failed.total()), style="bold")
    return output


def summary(
    progress: Progress,
    found: Counter,
    checked: Counter,
    failed: Counter,
) -> Group:
    return Group(progress, table(found, checked, failed))


def clear(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        (path / name).unlink(missing_ok=True)


def save(errors: list[Error], path: Path) -> None:
    if not errors:
        return

    with path.open("w", encoding="utf-8") as file:
        for error in sorted(errors, key=lambda item: item.path):
            record = {"path": error.path, "error": error.error}
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run(cfg: Config, console: Console) -> int:
    assets = files.find_assets(cfg, console)
    asset_found = Counter(asset.format for asset in assets)
    relation_sources = relations.find(cfg.path)
    relation_found = relations.found(relation_sources, cfg.formats)
    found = asset_found + relation_found
    checked: Counter = Counter()
    failed: Counter = Counter()
    errors: list[Error] = []

    progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )
    task = progress.add_task("Checking", total=len(assets) + relation_found.total())

    clear(cfg.reports)
    output = stats.Writer(cfg.reports) if cfg.stats else nullcontext()
    initial = summary(progress, found, checked, failed)
    with output as writer, Live(initial, console=console, refresh_per_second=10) as live:
        updated = time.monotonic()

        def refresh(force: bool = False) -> None:
            live.update(
                summary(progress, found, checked, failed),
                refresh=force,
            )

        results = chain(
            files.decode_assets(assets, cfg),
            relations.validate(relation_sources, cfg.path, set(relation_found)),
        )
        for result in results:
            checked[result.format] += 1
            if result.error:
                failed[result.format] += 1
                errors.append(result.error)
            elif writer and result.records:
                writer.write(result.records)

            progress.advance(task)
            now = time.monotonic()
            if now - updated >= 0.1:
                refresh()
                updated = now

        refresh(force=True)

        if writer:
            writer.formats(asset_found, checked, failed)

    save(errors, cfg.reports / ERRORS_JSONL)

    if errors:
        console.print(f"⛔ [red]{len(errors)} errors written to '{cfg.reports / ERRORS_JSONL}'[/]")
        return 1

    console.print("✅ [green]No errors found.[/]")
    return 0


@tools.command()
@click.argument(
    "PATH",
    required=False,
    type=click.Path(path_type=Path, file_okay=False),
)
@click.option(
    "-F",
    "--formats",
    type=click.Choice(FORMATS, case_sensitive=False),
    multiple=True,
    help="Formats to check. Repeat for multiple formats.",
)
@click.option(
    "-W",
    "--workers",
    type=click.IntRange(min=0),
    help="Worker threads. Use 0 to disable threads.",
)
@click.option(
    "--reports",
    type=click.Path(path_type=Path, file_okay=False),
    help="Reports directory.",
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
    workers: int | None,
    animation: bool | None,
    reports: Path | None,
    stats: bool | None,
) -> None:
    cfg = Config.load(path, formats, workers, animation, reports, stats)
    raise SystemExit(run(cfg, Console()))
