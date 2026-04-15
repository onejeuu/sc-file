import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QRunnable, QThreadPool
from rich import print

from scfile import convert, exceptions
from scfile.cli import utils
from scfile.consts import CLI
from scfile.core import UserOptions
from scfile.enums import L

from .base import Worker


@dataclass
class ConvertContext:
    options: UserOptions
    output: Path | None
    relative: bool
    predicate: Callable[[Path], bool]


class ConvertTask(QRunnable):
    def __init__(
        self,
        source: Path,
        output: Path | None,
        context: ConvertContext,
    ):
        super().__init__()
        self.source = source
        self.output = output
        self.context = context

    def run(self):
        try:
            convert.auto(source=self.source, output=self.output, options=self.context.options)
            print(f"{L.DONE} '{self.source.as_posix()}'")

        except exceptions.InvalidStructureError as err:
            print(f"{L.ERROR} {str(err)} {CLI.EXCEPTION}")

        except exceptions.ScFileException as err:
            print(f"{L.ERROR} {str(err)}")

        except Exception as err:
            print(f"{L.EXCEPTION} {str(err)}")


class ConvertDispatcher(Worker):
    def __init__(
        self,
        sources: list[Path],
        context: ConvertContext,
    ):
        super().__init__()
        self.sources = sources
        self.context = context
        self.pool = QThreadPool.globalInstance()

    def run(self):
        try:
            if self.context.output:
                self.context.output.mkdir(exist_ok=True, parents=True)

            for source in self.sources:
                if not source.exists():
                    print(f"{L.ERROR} Source not found '{source.as_posix()}'")

            for root, source in utils.paths_to_files_map(self.sources):
                if not self.context.predicate(source):
                    continue

                dest = utils.output_to_destination(
                    root,
                    source,
                    self.context.output,
                    self.context.relative,
                    parent=False,
                )

                task = ConvertTask(source, dest, self.context)
                self.pool.start(task)

        except Exception as err:
            print(f"{L.EXCEPTION} {repr(err)}")
            print(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()
            print(f"{L.DONE} Converting")
