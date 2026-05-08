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

from .shared import utils
from .shared.strings import Strings
from .shared.styles import Styles
from .tabs.convert import ConverterTab
from .tabs.mapcache import MapCacheTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs: dict[int, QWidget] = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowIcon(QIcon(str(utils.get_resource("assets/scfile.ico"))))
        self.setWindowTitle("scfile")
        self.setStyleSheet(Styles.WINDOW)
        self.resize(1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.tab_bar = QTabBar()
        self.tab_bar.setStyleSheet(Styles.TAB)
        self.tab_bar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.content_stack = QStackedWidget()

        self._add_tab(
            name=Strings.get("tab_converter"),
            widget=ConverterTab(),
        )
        self._add_tab(
            name=Strings.get("tab_mapcache"),
            widget=MapCacheTab(),
        )

        self.main_layout.addWidget(self.tab_bar)
        self.main_layout.addWidget(self.content_stack)
        self.main_layout.addWidget(FooterWidget())

        self._on_tab_changed(0)

    def _add_tab(self, name: str, widget: QWidget):
        index = self.tab_bar.addTab(name)
        self.content_stack.addWidget(widget)
        self.tabs[index] = widget

    def _on_tab_changed(self, index: int):
        if widget := self.tabs.get(index):
            self.content_stack.setCurrentWidget(widget)


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
