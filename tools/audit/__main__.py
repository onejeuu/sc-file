import json
import time
from collections import Counter
from pathlib import Path

import click
from rich.console import Console, Group
from rich.live import Live
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from tools.audit import files
from tools.audit.config import FORMATS, Config
from tools.audit.types import Error


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


def save(errors: list[Error], path: Path) -> None:
    if not errors:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for error in sorted(errors, key=lambda item: item.path):
            record = {"path": error.path, "error": error.error}
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run(cfg: Config, console: Console) -> int:
    assets = files.find_assets(cfg, console)
    found = Counter(asset.format for asset in assets)
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
    task = progress.add_task("Checking", total=len(assets))

    initial = Group(progress, table(found, checked, failed))
    with Live(initial, console=console, refresh_per_second=10) as live:
        updated = time.monotonic()

        for result in files.decode_assets(assets, cfg):
            checked[result.format] += 1
            if result.error:
                failed[result.format] += 1
                errors.append(result.error)

            progress.advance(task)
            now = time.monotonic()
            if now - updated >= 0.1:
                live.update(Group(progress, table(found, checked, failed)))
                updated = now

        live.update(Group(progress, table(found, checked, failed)), refresh=True)

    save(errors, cfg.log)
    if errors:
        console.print(f"[red]{len(errors)} errors written to '{cfg.log}'[/]")
        return 1

    console.print("[green]No errors found.[/]")
    return 0


@click.command()
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
    "--animation",
    type=bool,
    default=None,
    help="Parse model skeletons and animations.",
)
@click.option(
    "--log",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Error logs path.",
)
def main(
    path: Path | None,
    formats: tuple[str, ...],
    workers: int | None,
    animation: bool | None,
    log: Path | None,
) -> None:
    cfg = Config.load(path, formats, workers, animation, log)
    raise SystemExit(run(cfg, Console()))


if __name__ == "__main__":
    main()
