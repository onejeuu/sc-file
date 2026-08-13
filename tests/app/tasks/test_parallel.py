from collections.abc import Iterator
from threading import Event, Thread

from scfile.app.events import TaskError
from scfile.app.tasks import TaskContext
from scfile.app.tasks.parallel import parallel


def test_synchronous() -> None:
    error = TaskError(ValueError("broken"))
    calls: list[int] = []

    def operation(value: int) -> int:
        calls.append(value)
        return value * 2

    result = list(parallel([1, error, 2], operation, TaskContext(), workers=1))

    assert result == [2, error, 4]
    assert calls == [1, 2]


def test_synchronous_stop() -> None:
    context = TaskContext()

    def operation(value: int) -> int:
        context.stop()
        return value

    assert list(parallel(range(3), operation, context, workers=1)) == [0]


def test_parallel() -> None:
    result = list(parallel(range(8), lambda value: value * 2, TaskContext(), workers=2))

    assert len(result) == 8
    assert {value for value in result if isinstance(value, int)} == set(range(0, 16, 2))


def test_error() -> None:
    error = TaskError(ValueError("broken"))
    calls: list[int] = []

    def operation(value: int) -> int:
        calls.append(value)
        return value

    result = iter(parallel([error, 1], operation, TaskContext(), workers=2))

    assert next(result) is error
    assert calls == []
    assert list(result) == [1]


def test_parallel_stop() -> None:
    context = TaskContext()
    filled = Event()
    release = Event()
    consumed: list[int] = []
    result: list[int | TaskError] = []

    def items() -> Iterator[int]:
        for value in range(8):
            consumed.append(value)
            if len(consumed) == 4:
                filled.set()
            yield value

    def operation(value: int) -> int:
        release.wait()
        return value

    thread = Thread(target=result.extend, args=(parallel(items(), operation, context, workers=2),))
    thread.start()

    assert filled.wait(timeout=1)
    context.stop()
    release.set()
    thread.join(timeout=1)

    assert not thread.is_alive()
    assert consumed == [0, 1, 2, 3]


def test_parallel_stopped() -> None:
    context = TaskContext()
    context.stop()

    assert not list(parallel([1], lambda value: value, context, workers=2))
