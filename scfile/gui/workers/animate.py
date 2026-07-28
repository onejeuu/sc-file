import traceback
from pathlib import Path

from scfile import exceptions, operations
from scfile.consts import Text

from .base import Worker
from .logs import logger


class AnimateWorker(Worker):
    def __init__(
        self,
        animation: Path,
        models: list[Path],
        output: Path,
    ):
        super().__init__()
        self.animation = animation
        self.models = models
        self.output = output

    def run(self) -> None:
        try:
            operations.arms(
                self.animation,
                *self.models,
                output=self.output,
            )
            logger.done(f"'{self.animation}'")

        except exceptions.BinaryStructureError as err:
            logger.error(f"'{err.location or self.animation}': {err} {Text.EXCEPTION}")

        except exceptions.ScFileException as err:
            logger.error(f"'{err.location or self.animation}': {err}")

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.finished.emit()

    def stop(self) -> None:
        self.thread().requestInterruption()
        self.thread().quit()
        self.thread().wait()
