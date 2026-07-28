import traceback
from pathlib import Path

from scfile import convert, exceptions
from scfile.consts import Text

from .base import Worker
from .logs import logger


class LipsyncWorker(Worker):
    def __init__(
        self,
        animation: Path,
        model: Path,
        output: Path,
    ):
        super().__init__()
        self.animation = animation
        self.model = model
        self.output = output

    def run(self) -> None:
        try:
            convert.lipsync(
                self.animation,
                self.model,
                output=self.output,
            )
            logger.done(f"'{self.animation}'")

        except exceptions.InvalidStructureError as err:
            logger.error(f"{str(err)} {Text.EXCEPTION}")

        except exceptions.ScFileException as err:
            logger.error(str(err))

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.finished.emit()

    def stop(self) -> None:
        self.thread().requestInterruption()
        self.thread().quit()
        self.thread().wait()
