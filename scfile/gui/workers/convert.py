import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeAlias

from PySide6.QtCore import QRunnable, QThreadPool

from scfile import convert, exceptions
from scfile.cli import utils
from scfile.consts import CLI
from scfile.core import UserOptions

from .base import Worker
from .logs import logger


Predicate: TypeAlias = Callable[[Path], bool]


@dataclass
class ConvertContext:
    options: UserOptions
    output: Path | None
    relative: bool
    predicate: Predicate


class ConvertTask(QRunnable):
    def __init__(
        self,
        source: Path,
        output: Path | None,
        options: UserOptions,
    ):
        super().__init__()
        self.source = source
        self.output = output
        self.options = options

    def run(self):
        try:
            convert.auto(source=self.source, output=self.output, options=self.options)
            logger.done(f"'{self.source.as_posix()}'")

        except exceptions.InvalidStructureError as err:
            logger.error(f"{str(err)} {CLI.EXCEPTION}")

        except exceptions.ScFileException as err:
            logger.error(str(err))

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())


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
                    logger.error(f"Source not found '{source.as_posix()}'")

            for root, source in utils.paths_to_files_map(self.sources):
                if not self.context.predicate(source):
                    continue

                dest = utils.output_to_destination(
                    root=root,
                    source=source,
                    output=self.context.output,
                    relative=self.context.relative,
                    parent=self.context.relative,  # this is NOT a typo
                )

                task = ConvertTask(source, dest, self.context.options)
                self.pool.start(task)

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()
            logger.done("Converting\n")
