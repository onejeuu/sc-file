"""Single-file animation export task."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from scfile import exceptions, types

from .base import Context, Item, Summary, failure


type Operation = Callable[..., Path]


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for applying external animation data."""

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
        if context.stopped:
            return Summary("Animation Export", 1, 0, cancelled=True)

        try:
            output = self.operation(self.source, *self.models, output=self.output)
            context.emit(Item(source=source, outputs=(output,), written=1))
            return Summary("Animation Export", 1, 1, written=1)
        except exceptions.ScFileException as error:
            context.emit(failure(source, error))
        except Exception as error:
            context.emit(failure(source, error, unexpected=True))

        return Summary("Animation Export", 1, 1, failed=1)
