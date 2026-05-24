import os
import threading
import traceback
from pathlib import Path

from PySide6.QtCore import QRunnable, QThreadPool

from scfile import exceptions
from scfile.core import Options
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
        options: Options,
        cancelled: CancelEvent,
    ):
        super().__init__()
        self.key = key
        self.paths = paths
        self.output = output
        self.options = options
        self.cancelled = cancelled

    def run(self):
        try:
            filename, chunks = regions.merge(self.key, self.paths, self.output, self.options, self.cancelled)
            logger.done(f"{filename} merged {chunks} chunks")

        except exceptions.MergeInterrupted:
            pass

        except exceptions.RegionFileError as err:
            logger.error(str(err))

        except Exception as err:
            logger.error(f"Region ({self.key}): {repr(err)}")
            logger.message.emit(traceback.format_exc())


class MapCacheWorker(Worker):
    def __init__(
        self,
        source: Path,
        output: Path,
        options: Options,
    ):
        super().__init__()
        self.source = source
        self.output = output
        self.options = options
        self.pool = QThreadPool()
        self.cancelled = threading.Event()

    def run(self) -> None:
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

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.pool.waitForDone()
            self.finished.emit()

            if self.thread().isInterruptionRequested():
                logger.aborted("Regions Merging\n")
            else:
                logger.done("Regions Merging\n")

    def stop(self):
        self.cancelled.set()
        self.pool.clear()
        self.thread().requestInterruption()
        self.thread().quit()
        self.thread().wait()
