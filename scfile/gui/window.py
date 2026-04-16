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

from scfile import __version__
from scfile.gui.tabs.retarget import RetargetTab

from .shared import utils
from .shared.strings import Strings
from .shared.styles import Styles
from .tabs.convert import ConverterTab
from .tabs.mapcache import MapCacheTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs: dict[int, tuple[QWidget, tuple[int, int]]] = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowIcon(QIcon(str(utils.get_resource("assets/scfile.ico"))))
        self.setWindowTitle(f"scfile {__version__}")
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

        # TODO: resize
        self._add_tab(
            name=Strings.get("tab_mapcache"),
            widget=MapCacheTab(),
            size=(1000, 480),
        )
        self._add_tab(
            name=Strings.get("tab_converter"),
            widget=ConverterTab(),
            size=(1000, 720),
        )
        self._add_tab(
            name=Strings.get("tab_retarget"),
            widget=RetargetTab(),
            size=(1000, 500),
        )

        self.main_layout.addWidget(self.tab_bar)
        self.main_layout.addWidget(self.content_stack)

        self._on_tab_changed(0)

    def _add_tab(self, name: str, widget: QWidget, size: tuple[int, int]):
        index = self.tab_bar.addTab(name)
        self.content_stack.addWidget(widget)
        self.tabs[index] = (widget, size)

    def _on_tab_changed(self, index: int):
        if data := self.tabs.get(index):
            widget, (w, h) = data
            self.content_stack.setCurrentWidget(widget)


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
