"""Bounded parallel task work."""

import os
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

from .execution import TaskContext


def parallel[Input, Output](
    items: Iterable[Input],
    operation: Callable[[Input], Output],
    context: TaskContext,
    workers: int | None = None,
) -> Iterator[Output]:
    """Process a stream with a bounded number of pending operations."""

    max_workers = workers if workers is not None else (os.cpu_count() or 4)
    if max_workers <= 1:
        # Keep explicit single-worker runs synchronous
        for item in items:
            if context.stopped:
                break
            yield operation(item)
        return

    source = iter(items)

    # Bound prefetched work
    limit = max_workers * 2

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending: set[Future[Output]] = set()

        def submit() -> bool:
            # Keep source consumption behind the same cancellation boundary as submission
            if context.stopped:
                return False

            try:
                item = next(source)
            except StopIteration:
                return False

            pending.add(executor.submit(operation, item))
            return True

        # Prime the scheduler without exhausting the streamed source
        while len(pending) < limit and submit():
            pass

        # Reuse freed capacity until the source ends or cancellation is requested
        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                yield future.result()

            if context.stopped:
                # Running calls finish under executor ownership
                # Only queued work can be cancelled
                for future in pending:
                    future.cancel()
                break

            # Refill only after completed work has left the bounded queue
            while len(pending) < limit and submit():
                pass
