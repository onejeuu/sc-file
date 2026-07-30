import traceback
from pathlib import Path

from scfile import exceptions, operations
from scfile.consts import INVALID_INPUT_HINT

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
            operations.face(
                self.animation,
                self.model,
                output=self.output,
            )
            logger.done(f"'{self.animation}'")

        except exceptions.BinaryStructureError as err:
            logger.error(f"'{err.location or self.animation}': {err} {INVALID_INPUT_HINT}")

        except exceptions.ScFileException as err:
            logger.error(f"'{err.location or self.animation}': {err}")

        except Exception as err:
            logger.exception(repr(err))
            logger.message.emit(traceback.format_exc())

        finally:
            self.finished.emit()
