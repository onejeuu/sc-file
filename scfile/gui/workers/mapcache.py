import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rich import print

from scfile.cli.cmd.mapcache import RegionKey, merge
from scfile.core.context.options import UserOptions
from scfile.enums import L

from .base import Worker


class MapCacheWorker(Worker):
    def __init__(
        self,
        source: Path,
        output: Path,
        options: UserOptions,
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
                print(L.ERROR, f"No MDAT files found in '{self.source}'")
                self.finished.emit()
                return

            regions: dict[RegionKey, list[Path]] = defaultdict(list)
            for path in mdats:
                rx, rz = map(int, path.stem.lstrip("reg.").split("."))
                regions[(rx, rz)].append(path)

            print(L.INFO, f"Found {len(regions)} unique regions")
            print(L.INFO, "Starting merge")

            # TODO: custom slider?
            max_workers = os.cpu_count() or 4

            # TODO: move to QThreadPool and QRunnable?
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                list(executor.map(lambda item: merge(item, self.output, self.options), regions.items()))

            print(L.DONE, "Merge")
            self.finished.emit()

        except Exception as err:
            print(L.ERROR, repr(err))
            self.finished.emit()
