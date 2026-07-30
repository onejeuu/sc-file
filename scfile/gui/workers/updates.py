from PySide6.QtCore import Signal

from scfile import __version__ as SEMVER
from scfile.enums import UpdateStatus
from scfile.utils import updates

from .base import Worker


class UpdatesWorker(Worker):
    status = Signal(UpdateStatus, str, str)

    def run(self) -> None:
        try:
            status, message, url = updates.check(SEMVER)
            self.status.emit(status, message, url)

        finally:
            self.finished.emit()
