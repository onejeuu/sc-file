from collections.abc import Callable
from functools import partial
from pathlib import Path

import click
from rich.console import Console
from rich.filesize import decimal
from rich.table import Table

from scfile.convert import converters, decoders, detect, encoders, registry
from scfile.core import Options
from tools.profile import profiler


ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "assets" / "profile" / "model.mcsb"
REPORTS = ROOT / "reports" / "profile"
DECODERS = decoders()
ENCODERS = encoders()
REGISTRY = registry()
PROFILES = tuple(
    sorted(
        {f"{source}-decode.prof" for source in DECODERS}
        | {f"{source}-{target}.prof" for source, targets in REGISTRY.items() for target in targets}
    )
)


def table(rows: list[tuple[str, float, int, Path]], count: int) -> Table:
    output = Table()
    output.add_column("Operation")
    output.add_column("Runs", justify="right")
    output.add_column("Total", justify="right")
    output.add_column("Average", justify="right", style="green")
    output.add_column("Calls", justify="right")
    output.add_column("Profile", style="cyan")

    for operation, elapsed, calls, profile in rows:
        output.add_row(
            operation,
            str(count),
            f"{elapsed:.3f} s",
            f"{elapsed / count:.3f} s",
            f"{calls:,}",
            profile.name,
        )

    return output


def clear(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for name in PROFILES:
        (path / name).unlink(missing_ok=True)


@click.command()
@click.argument(
    "SOURCE",
    required=False,
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "-T",
    "--target",
    multiple=True,
    help="Output format. Repeat or use 'full'.",
)
@click.option(
    "-N",
    "--count",
    type=click.IntRange(min=1),
    default=1,
    show_default=True,
    help="Number of runs.",
)
@click.option(
    "--sort",
    type=click.Choice(("time", "cumulative", "calls"), case_sensitive=False),
    default="time",
    show_default=True,
    help="Profile sorting.",
)
@click.option(
    "--limit",
    type=click.IntRange(min=1),
    default=30,
    show_default=True,
    help="Functions to print.",
)
@click.option(
    "--animation",
    is_flag=True,
    help="Parse model skeletons and animations.",
)
@click.option(
    "--reports",
    type=click.Path(path_type=Path, file_okay=False),
    help="Reports directory.",
)
def main(
    source: Path | None,
    target: tuple[str, ...],
    count: int,
    sort: str,
    limit: int,
    animation: bool,
    reports: Path | None,
) -> None:
    reports = reports or REPORTS
    if not reports.is_absolute():
        reports = ROOT / reports
    reports = reports.resolve()

    options = Options(skeleton=animation, animation=animation)
    source = source or MODEL
    if not source.is_file():
        raise click.UsageError(f"Reference file not found: '{source}'.")

    source_format = detect.format(source)
    decoder = DECODERS.get(source_format)
    if decoder is None:
        raise click.UsageError(f"Unsupported source format: '{source_format}'.")

    available = converters(source_format)
    targets = tuple(dict.fromkeys(value.lower().lstrip(".") for value in target))
    if "full" in targets:
        targets = tuple(sorted(available))

    unsupported = tuple(value for value in targets if value not in available)
    if unsupported:
        supported = ", ".join(sorted(available)) or "none"
        raise click.UsageError(
            f"Unsupported conversion: '{source_format}' to '{unsupported[0]}'. Available: {supported}."
        )

    cases: list[tuple[str, Callable[[], None], Path]] = []
    if targets:
        for value in targets:
            name = f"{source_format} to {value}"
            operation = partial(profiler.convert, source, decoder, ENCODERS[value], options)
            cases.append((name, operation, reports / f"{source_format}-{value}.prof"))
    else:
        name = f"{source_format} decode"
        operation = partial(profiler.decode, source, decoder, options)
        cases.append((name, operation, reports / f"{source_format}-decode.prof"))

    clear(reports)
    rows = []
    stats = []
    for name, operation, report in cases:
        result, elapsed, calls = profiler.run(operation, count, report)
        stats.append(result)
        rows.append((name, elapsed, calls, report))

    console = Console()
    console.print(f"[cyan]{source}[/] ({decimal(source.stat().st_size)})")
    console.print(table(rows, count))
    console.print(f"\nProfiles written to '{reports}'.")

    if len(stats) == 1:
        console.print()
        stats[0].strip_dirs().sort_stats(sort).print_stats(limit)


if __name__ == "__main__":
    main()
