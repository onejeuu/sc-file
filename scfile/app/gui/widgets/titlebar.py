from typing import override

from PySide6.QtCore import QEvent, QObject, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPainterPath, QPixmap, QRegion
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QWidget

from scfile.app import files
from scfile.app.gui.styles import Colors, Styles


class TitleBar(QWidget):
    def __init__(self, qwindow: QMainWindow):
        super().__init__(qwindow)
        self.qwindow = qwindow
        self.setObjectName("titleBar")
        self.setFixedHeight(32)
        self.setStyleSheet(Styles.TITLE_BAR)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand = QWidget()
        brand.setObjectName("titleBrand")
        brand.setFixedWidth(56)
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        icon = QLabel()
        icon.setObjectName("windowIcon")
        icon.setPixmap(qwindow.windowIcon().pixmap(18, 18))
        icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        brand_layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(brand)

        title = QLabel(qwindow.windowTitle())
        title.setObjectName("windowTitle")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addSpacing(12)
        layout.addWidget(title)
        layout.addStretch()

        self.minimize = self._button("minimize", "minimizeButton", qwindow.showMinimized)
        self.maximize = self._button("maximize", "maximizeButton", self._toggle_maximized)
        self.close_button = self._button("close", "closeButton", qwindow.close)
        layout.addWidget(self.minimize)
        layout.addWidget(self.maximize)
        layout.addWidget(self.close_button)

        qwindow.installEventFilter(self)

    def _button(self, icon: str, name: str, action) -> QPushButton:
        button = QPushButton()
        button.setObjectName(name)
        button.setFixedSize(42, 31)
        button.setCursor(Qt.CursorShape.ArrowCursor)
        button.setIcon(_icon(icon))
        button.setIconSize(QSize(14, 14))
        button.clicked.connect(action)
        return button

    def _toggle_maximized(self) -> None:
        self.qwindow.showNormal() if self.qwindow.isMaximized() else self.qwindow.showMaximized()

    def _sync_maximize(self) -> None:
        self.maximize.setIcon(_icon("restore" if self.qwindow.isMaximized() else "maximize"))

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is getattr(self, "qwindow", None) and event.type() == QEvent.Type.WindowStateChange:
            self._sync_maximize()
        return super().eventFilter(watched, event)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.qwindow.windowHandle()
            if handle is not None:
                handle.startSystemMove()
            event.accept()
            return
        super().mousePressEvent(event)

    @override
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class WindowResizeFrame(QObject):
    def __init__(self, qwindow: QMainWindow, surface: QWidget):
        self.qwindow = qwindow
        self.surface = surface
        super().__init__(surface)
        self.handles = tuple(_ResizeHandle(qwindow, surface, edges) for edges in _EDGES)
        surface.installEventFilter(self)
        qwindow.installEventFilter(self)
        self._layout()

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        surface = getattr(self, "surface", None)
        qwindow = getattr(self, "qwindow", None)
        if watched is surface and event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self._layout()
        elif watched is qwindow and event.type() == QEvent.Type.WindowStateChange:
            self._layout()
        return super().eventFilter(watched, event)

    def _layout(self) -> None:
        width = self.surface.width()
        height = self.surface.height()
        edge = 5
        corner = 10
        geometries = (
            (corner, 0, max(0, width - corner * 2), edge),
            (corner, height - edge, max(0, width - corner * 2), edge),
            (0, corner, edge, max(0, height - corner * 2)),
            (width - edge, corner, edge, max(0, height - corner * 2)),
            (0, 0, corner, corner),
            (width - corner, 0, corner, corner),
            (0, height - corner, corner, corner),
            (width - corner, height - corner, corner, corner),
        )
        visible = not self.qwindow.isMaximized() and not self.qwindow.isFullScreen()
        maximized = not visible
        if self.surface.property("maximized") != maximized:
            self.surface.setProperty("maximized", maximized)
            style = self.surface.style()
            style.unpolish(self.surface)
            style.polish(self.surface)
        if visible:
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.qwindow.rect()), 8, 8)
            self.qwindow.setMask(QRegion(path.toFillPolygon().toPolygon()))
        else:
            self.qwindow.clearMask()
        for handle, geometry in zip(self.handles, geometries, strict=True):
            handle.setGeometry(*geometry)
            handle.setVisible(visible)
            handle.raise_()


class _ResizeHandle(QWidget):
    def __init__(self, qwindow: QMainWindow, parent: QWidget, edges: Qt.Edge):
        super().__init__(parent)
        self.qwindow = qwindow
        self.edges = edges
        self.setCursor(_CURSORS[edges])

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.qwindow.windowHandle()
            if handle is not None:
                handle.startSystemResize(self.edges)
            event.accept()
            return
        super().mousePressEvent(event)


_EDGES = (
    Qt.Edge.TopEdge,
    Qt.Edge.BottomEdge,
    Qt.Edge.LeftEdge,
    Qt.Edge.RightEdge,
    Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
    Qt.Edge.TopEdge | Qt.Edge.RightEdge,
    Qt.Edge.BottomEdge | Qt.Edge.LeftEdge,
    Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
)

_CURSORS = {
    Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
    Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
    Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
    Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
    Qt.Edge.TopEdge | Qt.Edge.LeftEdge: Qt.CursorShape.SizeFDiagCursor,
    Qt.Edge.TopEdge | Qt.Edge.RightEdge: Qt.CursorShape.SizeBDiagCursor,
    Qt.Edge.BottomEdge | Qt.Edge.LeftEdge: Qt.CursorShape.SizeBDiagCursor,
    Qt.Edge.BottomEdge | Qt.Edge.RightEdge: Qt.CursorShape.SizeFDiagCursor,
}


def _icon(name: str) -> QIcon:
    source = QPixmap(str(files.resource(f"assets/window.{name}.png")))
    icon = QIcon()
    icon.addPixmap(_tint(source, Colors.TEXT_SECONDARY.value), QIcon.Mode.Normal)
    icon.addPixmap(_tint(source, Colors.TEXT.value), QIcon.Mode.Active)
    return icon


def _tint(source: QPixmap, color: QColor) -> QPixmap:
    tinted = QPixmap(source.size())
    tinted.fill(Qt.GlobalColor.transparent)
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, source)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), color)
    painter.end()
    return tinted
