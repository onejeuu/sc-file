import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import override

from PySide6.QtCore import QRunnable, QThreadPool

from scfile import convert, exceptions, types
from scfile.consts import INVALID_INPUT_HINT
from scfile.options import ConvertOptions
from scfile.utils import files

from .base import Worker
from .logs import logger


@dataclass
class ConvertContext:
    whitelist: types.FilesWhitelist
    options: ConvertOptions
    output: Path | None
    relative: bool


class ConvertTask(QRunnable):
    def __init__(
        self,
        src: str,
        dst: str | None,
        options: ConvertOptions,
    ):
        super().__init__()
        self.src = src
        self.dst = dst
        self.options = options

    @override
    def run(self):
        try:
            results = convert.files.auto(source=self.src, output=self.dst, options=self.options)
            if any(result.status is convert.files.Status.WRITTEN for result in results):
                logger.done(f"'{self.src}'")
            else:
                logger.info(f"Skipped '{self.src}'")

        except exceptions.BinaryStructureError as err:
            logger.error(f"'{err.location or self.src}': {err} {INVALID_INPUT_HINT}")

        except exceptions.ScFileException as err:
            logger.error(f"'{err.location or self.src}': {err}")

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())


class ConvertWorker(Worker):
    def __init__(
        self,
        sources: list[str],
        context: ConvertContext,
    ):
        super().__init__()
        self.sources = sources
        self.context = context
        self.pool = QThreadPool()

    @override
    def run(self):
        completed = False

        try:
            if self.context.output:
                self.context.output.mkdir(exist_ok=True, parents=True)

            output = str(self.context.output) if self.context.output else None

            for entry in files.walk(self.sources, whitelist=self.context.whitelist, parent=self.context.relative):
                if self.thread().isInterruptionRequested():
                    self.pool.clear()
                    break

                dst = files.destination(relpath=entry.relpath, relative=self.context.relative, output=output)
                self.pool.start(ConvertTask(src=entry.path, dst=dst, options=self.context.options))

            completed = not self.thread().isInterruptionRequested()

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()

            if self.thread().isInterruptionRequested():
                logger.aborted("Converting\n")
            elif completed:
                logger.done("Converting\n")

    def stop(self) -> None:
        self.pool.clear()
