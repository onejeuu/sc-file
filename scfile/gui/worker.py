from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, Signal
from rich import print

from scfile import convert, exceptions
from scfile.cli import utils
from scfile.cli.types import FilesPaths
from scfile.consts import CLI
from scfile.core.context.options import UserOptions
from scfile.enums import L


@dataclass
class OutputConfig:
    path: Path | None
    relative: bool
    parent: bool


class ConvertWorker(QObject):
    finished = Signal()

    def __init__(
        self,
        sources: FilesPaths,
        options: UserOptions,
        output: OutputConfig,
        predicate: Callable[[Path], bool],
    ):
        super().__init__()
        self._sources = sources
        self._options = options
        self._output = output
        self._predicate = predicate
        self._is_running = True

    def run(self):
        try:
            for root, source in utils.paths_to_files_map(self._sources):
                if not self._predicate(source):
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
                    print(f"{L.ERROR} {str(err)} {CLI.EXCEPTION}")

                except exceptions.ScFileException as err:
                    print(f"{L.ERROR} {str(err)}")

                except Exception as err:
                    print(f"{L.EXCEPTION} {str(err)}")

                else:
                    print(f"{L.DONE} '{source.as_posix()}'")

        finally:
            print(f"{L.DONE} CONVERTING\n")
            self.finished.emit()
