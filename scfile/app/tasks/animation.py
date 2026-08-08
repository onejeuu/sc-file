"""Single-file animation export task."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from scfile import exceptions, types
from scfile.options import Options

from .base import Context, Item, Started, Summary, TaskKind, failure


type Operation = Callable[..., types.ResultPath]


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for applying external animation data."""

    kind: ClassVar[TaskKind] = TaskKind.ANIMATE

    operation: Operation
    source: Path
    models: tuple[Path, ...]
    output: Path
    options: Options = field(default_factory=Options)

    def run(
        self,
        context: Context,
    ) -> Summary:
        """Apply animation data and report its output."""

        output = self.output.resolve()
        context.emit(Started(self.kind, 1, output))

        src = str(self.source)

        if context.stopped:
            return Summary(self.kind, 1, 0, cancelled=True, output=output)

        try:
            result = self.operation(self.source, *self.models, output=self.output, options=self.options)
            if result is None:
                context.emit(Item(source=src, skipped=1))
                return Summary(self.kind, 1, 1, skipped=1, output=output)

            output = result.resolve()
            context.emit(Item(source=src, outputs=(output,), written=1))
            return Summary(self.kind, 1, 1, succeeded=1, written=1, output=output)
        except exceptions.ScFileException as error:
            context.emit(failure(src, error))
        except Exception as error:
            context.emit(failure(src, error, unexpected=True))

        return Summary(self.kind, 1, 1, failed=1, output=output)
