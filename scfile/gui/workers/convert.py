import traceback
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRunnable, QThreadPool

from scfile import convert, exceptions, types
from scfile.consts import CLI
from scfile.core import UserOptions
from scfile.utils import files

from .base import Worker
from .logs import logger


@dataclass
class ConvertContext:
    whitelist: types.FilesWhitelist
    options: UserOptions
    output: Path | None
    relative: bool


class ConvertTask(QRunnable):
    def __init__(
        self,
        src: str,
        dst: str | None,
        options: UserOptions,
    ):
        super().__init__()
        self.src = src
        self.dst = dst
        self.options = options

    def run(self):
        try:
            convert.auto(source=self.src, output=self.dst, options=self.options)
            logger.done(f"'{self.src}'")

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
        sources: list[str],
        context: ConvertContext,
    ):
        super().__init__()
        self.sources = sources
        self.context = context
        self.pool = QThreadPool()

    def run(self):
        try:
            if self.context.output:
                self.context.output.mkdir(exist_ok=True, parents=True)

            output = str(self.context.output) if self.context.output else None

            for entry in files.walk(self.sources, whitelist=self.context.whitelist, parent=self.context.relative):
                dst = files.destination(relpath=entry.relpath, relative=self.context.relative, output=output)
                self.pool.start(ConvertTask(src=entry.path, dst=dst, options=self.context.options))

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()
            logger.done("Converting\n")
