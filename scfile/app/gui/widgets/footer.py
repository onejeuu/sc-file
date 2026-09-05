from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from scfile import __repository__ as REPO
from scfile.app.gui import strings
from scfile.app.gui.styles import Styles
from scfile.app.localization import DOCS_URL

from .link import LinkWidget


class FooterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("footer")
        self.setStyleSheet(Styles.FOOTER)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        links = QWidget()
        links_layout = QHBoxLayout(links)
        links_layout.setContentsMargins(16, 8, 16, 8)
        links_layout.setSpacing(10)

        repo = LinkWidget(text=f"{REPO}", url=f"https://github.com/{REPO}")
        docs = LinkWidget(text=strings.get("label.footer.docs"), url=DOCS_URL)

        links_layout.addWidget(repo)
        links_layout.addWidget(docs)
        links_layout.addStretch()

        self.section_help = LinkWidget(text=strings.get("label.footer.guide"), url="")
        self.section_help.hide()
        links_layout.addWidget(self.section_help)

        layout.addWidget(links)

    def set_section_help(self, url: str | None) -> None:
        self.section_help.url = url or ""
        self.section_help.setVisible(bool(url))
