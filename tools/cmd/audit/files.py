import time
from collections import defaultdict
from functools import partial
from pathlib import Path

from rich.console import Console

from scfile import convert, formats
from scfile.app import files
from scfile.app.events import TaskError
from scfile.enums import FileFormat
from scfile.exceptions import EmptyFileError
from scfile.options import Options

from . import stats
from .rules import EXCLUDED
from .runner import Case, Plan, Suite, Warning


DECODERS = {str(format): decoder for format, decoder in formats.registry.decoders.items()}


def decode(
    root: Path,
    path: Path,
    format: str,
    options: Options,
    statistics: bool,
) -> list[stats.Record]:
    try:
        with DECODERS[format](path, options) as decoder:
            content = decoder.decode()

    except EmptyFileError:
        return []

    return stats.records(root, path, content, options.model.animation) if statistics else []


def build(
    root: Path,
    selected: tuple[str, ...],
    configured_excludes: tuple[str, ...],
    animation: bool,
    statistics: bool,
    console: Console,
) -> Plan:
    if not selected:
        return Plan()

    grouped: defaultdict[str, list[Path]] = defaultdict(list)
    warnings: list[Warning] = []
    ignored = 0
    excluded = EXCLUDED | set(configured_excludes)
    filters = formats.registry.filters(*(FileFormat(format) for format in selected))

    with console.status("Searching... 0 files") as status:
        updated = time.monotonic()
        found = 0

        for item in files.scan([root], filters):
            if isinstance(item, TaskError):
                warnings.append(
                    Warning(
                        "scan",
                        {"path": Path(item.source or root)},
                        f"{type(item.error).__name__}: {item.error}",
                    )
                )
                continue

            path = Path(item.path)
            relative = path.relative_to(root).as_posix().casefold()
            if relative in excluded:
                ignored += 1
                continue

            format = convert.files.format(path)
            grouped[format].append(path)
            found += 1

            now = time.monotonic()
            if now - updated >= 0.1:
                status.update(f"Searching... {found} files")
                updated = now

    options = Options(model=Options.Model(skeleton=animation, animation=animation))
    suites = []
    for format, paths in sorted(grouped.items()):
        paths.sort()
        cases = [
            Case(
                {"file": path},
                partial(decode, root, path, format, options, statistics),
            )
            for path in paths
        ]
        suites.append(Suite("file", format, len(paths), cases))

    notices = [f"Ignored {ignored} configured asset paths."] if ignored else []
    return Plan(suites, warnings, notices)
