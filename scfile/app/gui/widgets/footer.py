from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from scfile import __repository__ as REPO
from scfile.app.gui import strings
from scfile.app.localization import DOCS_URL

from .link import LinkWidget
from .updates import VersionWidget


class FooterWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        links = QWidget()
        links_layout = QHBoxLayout(links)
        links_layout.setContentsMargins(10, 0, 10, 5)
        links_layout.setSpacing(10)

        self.version = VersionWidget()
        repo = LinkWidget(text=f"{REPO}", url=f"https://github.com/{REPO}")
        docs = LinkWidget(text=strings.get("label.documentation"), url=DOCS_URL)

        links_layout.addWidget(self.version)
        links_layout.addWidget(repo)
        links_layout.addWidget(docs)
        links_layout.addStretch()

        layout.addWidget(links)

    def stop(self) -> None:
        self.version.stop()
