import os
import threading
import traceback
from pathlib import Path
from typing import override

from PySide6.QtCore import QRunnable, QThreadPool

from scfile import exceptions
from scfile.options import HandlerOptions
from scfile.utils import regions
from scfile.utils.regions import CancelEvent, RegionKey

from .base import Worker
from .logs import logger


class MergeTask(QRunnable):
    def __init__(
        self,
        key: RegionKey,
        paths: list[Path],
        output: Path,
        options: HandlerOptions,
        cancelled: CancelEvent,
    ):
        super().__init__()
        self.key = key
        self.paths = paths
        self.output = output
        self.options = options
        self.cancelled = cancelled

    @override
    def run(self):
        try:
            filename, chunks = regions.merge(self.key, self.paths, self.output, self.options, self.cancelled)
            logger.done(f"{filename} merged {chunks} chunks")

        except exceptions.MergeInterrupted:
            pass

        except exceptions.RegionFileError as err:
            logger.error(f"'{err.location}': {err}")

        except Exception as err:
            logger.error(f"Region ({self.key}): {repr(err)}")
            logger.message.emit(traceback.format_exc())


class MapCacheWorker(Worker):
    def __init__(
        self,
        source: Path,
        output: Path,
        options: HandlerOptions,
    ):
        super().__init__()
        self.source = source
        self.output = output
        self.options = options
        self.pool = QThreadPool()
        self.cancelled = threading.Event()

    @override
    def run(self) -> None:
        completed = False

        try:
            mdats = regions.resolve(self.source)
            if not mdats:
                logger.error(f"No MDAT files found in '{self.source}'")
                return

            mapping = regions.parse(mdats)
            if not mapping:
                logger.error(f"No valid regions found in '{self.source}'")
                return

            if not self.output.exists():
                self.output.mkdir(parents=True, exist_ok=True)

            logger.info(f"Found {len(mapping)} unique regions")
            logger.info("Starting merging...")

            self.pool.setMaxThreadCount((os.cpu_count() or 4) * 2)
            for key, paths in mapping.items():
                if self.thread().isInterruptionRequested():
                    self.pool.clear()
                    break
                task = MergeTask(key, paths, self.output, self.options, self.cancelled)
                self.pool.start(task)

            completed = not self.thread().isInterruptionRequested()

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()

            if self.thread().isInterruptionRequested():
                logger.aborted("Regions Merging\n")
            elif completed:
                logger.done("Regions Merging\n")

    def stop(self) -> None:
        self.cancelled.set()
        self.pool.clear()
