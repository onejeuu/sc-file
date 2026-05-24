import os
import traceback
from pathlib import Path

from PySide6.QtCore import QRunnable, QThreadPool

from scfile.cli.cmd import mapcache
from scfile.cli.cmd.mapcache import RegionKey, parse_regions
from scfile.core import Options

from .base import Worker
from .logs import logger


class MergeRegionTask(QRunnable):
    def __init__(
        self,
        key: RegionKey,
        paths: list[Path],
        output: Path,
        options: Options,
    ):
        super().__init__()
        self.key = key
        self.paths = paths
        self.output = output
        self.options = options

    def run(self):
        try:
            mapcache.merge(
                (self.key, self.paths),
                self.output,
                self.options,
                on_done=logger.done,
                on_error=logger.error,
            )

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

    def run(self) -> None:
        try:
            mdats = [
                path for path in self.source.rglob("*.mdat") if path.stat().st_size > 0 and ".bck" not in str(path)
            ]

            if not mdats:
                logger.error(f"No MDAT files found in '{self.source}'")
                return

            regions = parse_regions(mdats)

            if not regions:
                logger.error(f"No valid regions found in '{self.source}'")
                return

            if not self.output.exists():
                self.output.mkdir(parents=True, exist_ok=True)

            logger.info(f"Found {len(regions)} unique regions")
            logger.info("Starting merging...")

            pool = QThreadPool()
            pool.setMaxThreadCount((os.cpu_count() or 4) * 2)
            for key, paths in regions.items():
                task = MergeRegionTask(key, paths, self.output, self.options)
                pool.start(task)

            pool.waitForDone()

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.finished.emit()
            logger.done("Merging\n")
