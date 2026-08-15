from collections.abc import Callable, Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tools.cmd.audit.schemas import Record


class PlanError(Exception):
    pass


@dataclass(frozen=True)
class Case:
    paths: dict[str, Path]
    check: Callable[[], list["Record"]]
    files: int = 1


@dataclass
class Suite:
    kind: str
    name: str
    cases: list[Case]

    @property
    def files(self) -> int:
        return sum(case.files for case in self.cases)


@dataclass(frozen=True)
class Warning:
    kind: str
    paths: dict[str, Path]
    message: str


@dataclass
class Plan:
    suites: list[Suite] = field(default_factory=list)
    warnings: list[Warning] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)

    def extend(self, other: "Plan") -> None:
        self.suites.extend(other.suites)
        self.warnings.extend(other.warnings)
        self.notices.extend(other.notices)


@dataclass(frozen=True)
class Passed:
    case: Case
    records: list["Record"]


@dataclass(frozen=True)
class Failed:
    case: Case
    error: Exception


type Result = Passed | Failed
type Item = tuple[Suite, Case]
type Execution = tuple[Suite, Result]


def _execute(item: Item) -> Execution:
    suite, case = item
    try:
        return suite, Passed(case, case.check())

    except Exception as error:
        return suite, Failed(case, error)


def run(suites: list[Suite], workers: int) -> Iterator[Execution]:
    items = ((suite, case) for suite in suites for case in suite.cases)

    if workers == 0:
        yield from map(_execute, items)
        return

    limit = max(workers * 2, 1)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending: set[Future[Execution]] = {executor.submit(_execute, item) for item in islice(items, limit)}

        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            pending.update(executor.submit(_execute, item) for item in islice(items, len(done)))
            for future in done:
                yield future.result()
