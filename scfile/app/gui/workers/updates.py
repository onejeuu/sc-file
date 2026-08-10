from typing import override

from PySide6.QtCore import Signal

from scfile import __version__ as SEMVER
from scfile.app.enums import UpdateStatus
from scfile.app import updates

from .base import Worker


class UpdatesWorker(Worker):
    status = Signal(UpdateStatus, str, str)

    @override
    def run(self) -> None:
        try:
            status, message, url = updates.check(SEMVER)
            self.status.emit(status, message, url)

        finally:
            self.finished.emit()
