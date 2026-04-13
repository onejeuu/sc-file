from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, Signal

from scfile import convert, exceptions
from scfile.cli import utils
from scfile.cli.types import FilesPaths
from scfile.consts import CLI
from scfile.core.context.options import UserOptions


@dataclass
class OutputConfig:
    path: Path | None
    relative: bool
    parent: bool


class ConvertWorker(QObject):
    logs = Signal(str)
    progress = Signal(int, int)
    finished = Signal()

    def __init__(
        self,
        sources: FilesPaths,
        options: UserOptions,
        output: OutputConfig,
        filter: Callable[[Path], bool],
    ):
        super().__init__()
        self._sources = sources
        self._options = options
        self._output = output
        self._filter = filter
        self._is_running = True

    def run(self):
        try:
            for root, source in utils.paths_to_files_map(self._sources):
                if not self._filter(source):
                    continue

                try:
                    dest = utils.output_to_destination(
                        root,
                        source,
                        self._output.path,
                        self._output.relative,
                        self._output.parent,
                    )

                    convert.auto(source=source, output=dest, options=self._options)

                except exceptions.InvalidStructureError as err:
                    self.logs.emit(f"ERROR: {str(err)} {CLI.EXCEPTION}")

                except exceptions.ScFileException as err:
                    self.logs.emit(f"ERROR: {str(err)}")

                except Exception as err:
                    self.logs.emit(f"UNEXPECTED ERROR: {repr(err)}")

                else:
                    self.logs.emit(f"DONE: {source.as_posix()}")

        finally:
            self.logs.emit("DONE: CONVERT")
            self.finished.emit()
