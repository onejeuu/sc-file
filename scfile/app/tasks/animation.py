"""Single-file animation export task."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import exceptions, types

from .base import Context, Item, Started, Summary, TaskKind, failure


type Operation = Callable[..., Path]


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for applying external animation data."""

    kind: ClassVar[TaskKind] = TaskKind.ANIMATE

    operation: Operation
    source: types.PathLike
    models: tuple[types.PathLike, ...]
    output: types.PathLike

    def run(
        self,
        context: Context,
    ) -> Summary:
        """Apply animation data and report its output."""

        source = str(self.source)
        output = Path(self.output).resolve()
        context.emit(Started(self.kind, 1, output))
        if context.stopped:
            return Summary(self.kind, 1, 0, cancelled=True, output=output)

        try:
            output = self.operation(self.source, *self.models, output=self.output)
            output = output.resolve()
            context.emit(Item(source=source, outputs=(output,), written=1))
            return Summary(self.kind, 1, 1, succeeded=1, written=1, output=output)
        except exceptions.ScFileException as error:
            context.emit(failure(source, error))
        except Exception as error:
            context.emit(failure(source, error, unexpected=True))

        return Summary(self.kind, 1, 1, failed=1, output=output)
