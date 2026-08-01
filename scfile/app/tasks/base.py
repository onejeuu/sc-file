"""Shared task contracts and execution helpers."""

import os
import traceback
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event as CancelEvent
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Progress:
    """Completed work relative to the known total."""

    completed: int
    total: int | None = None


@dataclass(frozen=True, slots=True)
class Item:
    """Result of processing one input item."""

    source: str
    outputs: tuple[Path, ...] = ()
    written: int = 0
    skipped: int = 0
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class Failure:
    """Failure associated with one input item."""

    source: str
    error: Exception
    traceback: str | None = None


type TaskEvent = Progress | Item | Failure
type Reporter = Callable[[TaskEvent], None]


def _ignore(_: TaskEvent) -> None: ...


@dataclass(slots=True)
class Context:
    """Cancellation and event reporting shared with a running task."""

    report: Reporter = _ignore
    cancelled: CancelEvent = field(default_factory=CancelEvent)

    @property
    def stopped(self) -> bool:
        return self.cancelled.is_set()

    def emit(self, event: TaskEvent) -> None:
        self.report(event)

    def stop(self) -> None:
        self.cancelled.set()


@dataclass(frozen=True, slots=True)
class Summary:
    """Aggregate result of a completed task."""

    name: str
    total: int
    completed: int
    written: int = 0
    skipped: int = 0
    failed: int = 0
    cancelled: bool = False


class Task(Protocol):
    """Application task executable with a shared context."""

    def run(
        self,
        context: Context,
    ) -> Summary: ...


def failure(
    source: str,
    error: Exception,
    *,
    unexpected: bool = False,
) -> Failure:
    """Create a task failure, retaining traceback for unexpected errors."""

    return Failure(
        source=source,
        error=error,
        traceback=traceback.format_exc() if unexpected else None,
    )


def parallel[Input, Output](
    items: Iterable[Input],
    operation: Callable[[Input], Output],
    context: Context,
    workers: int | None = None,
) -> Iterator[Output]:
    """Process a stream with a bounded number of pending operations."""

    max_workers = workers if workers is not None else (os.cpu_count() or 4)
    if max_workers <= 1:
        for item in items:
            if context.stopped:
                break
            yield operation(item)
        return

    source = iter(items)
    limit = max_workers * 2

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending: set[Future[Output]] = set()

        def submit() -> bool:
            if context.stopped:
                return False
            try:
                item = next(source)
            except StopIteration:
                return False
            pending.add(executor.submit(operation, item))
            return True

        while len(pending) < limit and submit():
            pass

        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                yield future.result()

            if context.stopped:
                for future in pending:
                    future.cancel()
                break

            while len(pending) < limit and submit():
                pass
