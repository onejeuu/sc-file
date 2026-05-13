import sys

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from scfile.gui.widgets.footer import FooterWidget
from scfile.utils import files

from .shared.strings import Str
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
        self.setWindowTitle("scfile")
        self.setStyleSheet(Styles.WINDOW)
        self.resize(1000, 700)

        group = QWidget()
        self.setCentralWidget(group)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabbar = QTabBar()
        self.tabbar.setStyleSheet(Styles.TAB)
        self.tabbar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tabbar.currentChanged.connect(self._on_tab_changed)

        self.stack = QStackedWidget()

        self._add_tab(
            name=Str.get("tab_converter"),
            widget=ConverterTab(),
        )
        self._add_tab(
            name=Str.get("tab_mapcache"),
            widget=MapCacheTab(),
        )

        layout.addWidget(self.tabbar)
        layout.addWidget(self.stack)
        layout.addWidget(FooterWidget())
        self._on_tab_changed(0)

    def _add_tab(self, name: str, widget: QWidget):
        index = self.tabbar.addTab(name)
        self.stack.addWidget(widget)
        self.tabs[index] = widget

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
