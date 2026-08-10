"""Bounded parallel task work."""

import os
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

from scfile.app.events import TaskError

from .execution import TaskContext


def parallel[Input, Output](
    items: Iterable[Input | TaskError],
    operation: Callable[[Input], Output],
    context: TaskContext,
    workers: int | None = None,
) -> Iterator[Output | TaskError]:
    """Process a stream with a bounded number of pending operations."""

    # Resolve worker count
    max_workers = workers if workers is not None else (os.cpu_count() or 4)
    if max_workers <= 1:
        yield from _synchronous(items, operation, context)
        return

    # Bound pending work window
    source = iter(items)
    limit = max_workers * 2

    # Run work concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending: set[Future[Output]] = set()
        exhausted = False

        while not context.stopped:
            # Keep source consumption bounded by available worker capacity
            while not exhausted and len(pending) < limit:
                try:
                    item = next(source)

                except StopIteration:
                    exhausted = True
                    break

                if isinstance(item, TaskError):
                    yield item
                    continue

                pending.add(executor.submit(operation, item))

            if not pending:
                break

            # Reclaim capacity before consuming more source items
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                yield future.result()

            if context.stopped:
                # Running calls finish under executor ownership
                for future in pending:
                    future.cancel()
                break


def _synchronous[Input, Output](
    items: Iterable[Input | TaskError],
    operation: Callable[[Input], Output],
    context: TaskContext,
) -> Iterator[Output | TaskError]:
    for item in items:
        if context.stopped:
            break
        if isinstance(item, TaskError):
            yield item
            continue
        yield operation(item)
