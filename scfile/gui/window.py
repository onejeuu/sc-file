import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from scfile.gui.widgets.footer import FooterWidget
from scfile.utils import files

from .shared import consts, strings
from .shared.styles import Styles
from .tabs.convert import ConverterTab
from .tabs.mapcache import MapCacheTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs: dict[int, QWidget] = {}
        self._build_ui()

    def _build_ui(self):
        self.setWindowIcon(QIcon(str(files.resource("assets/scfile.ico"))))
        self.setWindowTitle(consts.TITLE)
        self.setStyleSheet(Styles.WINDOW)
        self.resize(1000, 800)

        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(Styles.SIDEBAR)
        sidebar.setFixedWidth(54)

        self.sidebar = QVBoxLayout(sidebar)
        self.sidebar.setContentsMargins(0, 16, 0, 0)
        self.sidebar.setSpacing(8)
        self.sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()

        content_layout.addWidget(self.stack)
        content_layout.addWidget(FooterWidget())

        layout.addWidget(sidebar)
        layout.addWidget(content)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.idClicked.connect(self._on_tab_changed)

        self._add_tab(
            widget=ConverterTab(),
            name=strings.get("tab.converter"),
            icon="assets/converter.png",
        )
        self._add_tab(
            widget=MapCacheTab(),
            name=strings.get("tab.mapcache"),
            icon="assets/mapcache.png",
        )

        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)
            self._on_tab_changed(0)

    def _add_tab(self, widget: QWidget, name: str, icon: str):
        index = self.stack.count()
        self.stack.addWidget(widget)
        self.tabs[index] = widget

        btn = QPushButton()
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(Styles.SIDEBAR_ITEM)
        btn.setToolTip(name)

        btn.setIcon(QIcon(str(files.resource(icon))))
        btn.setIconSize(QSize(20, 20))

        self.sidebar.addWidget(btn)
        self.button_group.addButton(btn, index)

    def _on_tab_changed(self, index: int):
        if widget := self.tabs.get(index):
            self.stack.setCurrentWidget(widget)

    def closeEvent(self, event):
        for widget in self.tabs.values():
            widget.close()

        event.accept()


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
