import json
import os
import time
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

import click
from rich.console import Console, Group
from rich.live import Live
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from tools.paths import ROOT

from . import files, relations, runner, stats
from .config import Settings
from .runner import Failed, Passed, Plan, Result, Suite, Warning


REPORTS = ROOT / "reports" / "audit"
ERRORS = "errors.jsonl"
WARNINGS = "warnings.jsonl"
FILES = (*stats.FILES, ERRORS, WARNINGS)


@dataclass
class Row:
    suite: Suite
    checked: int = 0
    errors: int = 0


class Audit:
    def __init__(self, settings: Settings, console: Console):
        self.settings = settings
        self.console = console
        self.plan = Plan()
        self.rows: dict[str, Row] = {}
        self.failures: list[tuple[Suite, Failed]] = []
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        )
        self.task = self.progress.add_task("Checking", total=0)
        self.stack = ExitStack()
        self.writer: stats.Writer | None = None
        self.live: Live | None = None
        self.updated = time.monotonic()

    def run(self) -> int:
        settings = self.settings
        self.plan = files.build(
            settings.root,
            settings.formats,
            settings.exclude,
            settings.animation,
            settings.stats,
            self.console,
        )
        self.plan.extend(relations.build(settings.root, settings.relations))
        self.rows = {suite.name: Row(suite) for suite in self.plan.suites}
        self.progress.update(self.task, total=sum(len(suite.cases) for suite in self.plan.suites))

        with self:
            for suite, result in runner.run(self.plan.suites, settings.workers):
                self.record(suite, result)
        return self.finish()

    def __enter__(self):
        clear()
        if self.settings.stats and any(suite.kind == "file" for suite in self.plan.suites):
            self.writer = self.stack.enter_context(stats.Writer(REPORTS))
        self.live = self.stack.enter_context(Live(self.render(), console=self.console, refresh_per_second=10))
        return self

    def __exit__(self, *args):
        self.refresh(force=True)
        if self.writer is not None:
            rows = (
                (row.suite.name, row.suite.files, row.checked, row.errors)
                for row in self.rows.values()
                if row.suite.kind == "file"
            )
            self.writer.formats(rows)
        self.stack.close()

    def render(self) -> Group:
        table = Table()
        table.add_column("Format", style="cyan")
        table.add_column("Files", justify="right")
        table.add_column("Checked", justify="right", style="green")
        table.add_column("Errors", justify="right", style="red")

        for row in self.rows.values():
            table.add_row(row.suite.name, str(row.suite.files), str(row.checked), str(row.errors))

        table.add_section()
        table.add_row(
            "Total",
            str(sum(row.suite.files for row in self.rows.values())),
            str(sum(row.checked for row in self.rows.values())),
            str(sum(row.errors for row in self.rows.values())),
            style="bold",
        )
        return Group(self.progress, table)

    def refresh(self, force: bool = False) -> None:
        if self.live is not None:
            self.live.update(self.render(), refresh=force)

    def record(self, suite: Suite, result: Result) -> None:
        row = self.rows[suite.name]
        row.checked += 1

        match result:
            case Passed(records=records):
                if self.writer is not None and records:
                    self.writer.write(records)
            case Failed() as failure:
                row.errors += 1
                self.failures.append((suite, failure))

        self.progress.advance(self.task)
        now = time.monotonic()
        if now - self.updated >= 0.1:
            self.refresh()
            self.updated = now

    def finish(self) -> int:
        for notice in self.plan.notices:
            self.console.print(f"[dim]{notice}[/]")

        errors = [error(self.settings.root, suite, failure) for suite, failure in self.failures]
        warnings = [warning(self.settings.root, item) for item in self.plan.warnings]
        save(REPORTS / ERRORS, errors)
        save(REPORTS / WARNINGS, warnings)

        match errors:
            case []:
                self.console.print("✅ [green]No errors found.[/]")
            case _:
                self.console.print(f"⛔ [red]{len(errors)} errors written to '{REPORTS / ERRORS}'[/]")

        if warnings:
            self.console.print(f"⚠️ [yellow]{len(warnings)} warnings written to '{REPORTS / WARNINGS}'[/]")
        return int(bool(errors))


def clear() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        try:
            (REPORTS / name).unlink(missing_ok=True)

        except PermissionError:
            raise click.ClickException(
                f"Cannot overwrite '{REPORTS / name}'. Close the file or wait for another audit to finish."
            ) from None


def relative(root: Path, paths: dict[str, Path]) -> dict[str, str]:
    return {name: os.path.relpath(path, root).replace("\\", "/") for name, path in paths.items()}


def error(root: Path, suite: Suite, failure: Failed) -> dict:
    issue = failure.error
    return {
        "kind": suite.kind,
        "paths": relative(root, failure.case.paths),
        "error": f"{type(issue).__name__}: {issue}",
    }


def warning(root: Path, issue: Warning) -> dict:
    return {
        "kind": issue.kind,
        "paths": relative(root, issue.paths),
        "warning": issue.message,
    }


def save(path: Path, records: list[dict]) -> None:
    if not records:
        return

    records.sort(key=lambda record: (record["kind"], tuple(sorted(record["paths"].items()))))
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
