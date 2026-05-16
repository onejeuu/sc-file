from PySide6.QtCore import QThread, Signal

from scfile import __version__ as SEMVER
from scfile.enums import UpdateStatus
from scfile.utils import updates


class UpdatesWorker(QThread):
    status = Signal(UpdateStatus, str, str)

    def run(self):
        status, info, url = updates.check(SEMVER)
        self.status.emit(status, info, url)
