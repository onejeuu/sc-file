from PySide6.QtWidgets import QHBoxLayout, QWidget

from scfile import __repository__ as REPO

from .link import LinkWidget
from .version import VersionWidget


class FooterWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 5)
        layout.setSpacing(10)

        version = VersionWidget()
        repo = LinkWidget(text=f"{REPO}", url=f"https://github.com/{REPO}")

        layout.addWidget(version)
        layout.addWidget(repo)
        layout.addStretch()
