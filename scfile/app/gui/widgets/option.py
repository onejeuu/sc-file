from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QAbstractButton, QCheckBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from scfile.app.gui.styles import Styles
from scfile.app.gui.widgets.switch import Switch


class OptionWidget(QWidget):
    changed = Signal(bool)

    def __init__(
        self,
        text: str,
        hint: str | None = None,
        checked: bool = False,
        icon: QIcon | None = None,
    ):
        super().__init__()
        self._icon = icon is not None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.checkbox: QAbstractButton = Switch() if icon is not None else QCheckBox()
        if isinstance(self.checkbox, QCheckBox):
            self.checkbox.setStyleSheet(Styles.CHECKBOX)
            self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(checked)
        self.checkbox.toggled.connect(self.changed.emit)

        if icon is None:
            if hint:
                title = QLabel(text)
                title.setStyleSheet(Styles.OPTION_TITLE)
                title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                layout.addWidget(title)
                self.checkbox.setText(hint)
            else:
                self.checkbox.setText(text)

            self.checkbox.setStyleSheet(Styles.OPTION_CHECKBOX)
            layout.addWidget(self.checkbox)
            return

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        image = QLabel()
        image.setPixmap(icon.pixmap(QSize(20, 20)))
        image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        row.addWidget(image)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(2)
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold;")
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content.addWidget(label)
        if hint:
            description = QLabel(hint)
            description.setStyleSheet(Styles.DESCRIPTION)
            description.setWordWrap(True)
            description.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            content.addWidget(description)

        row.addLayout(content, 1)
        row.addWidget(self.checkbox)
        layout.addLayout(row)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._icon and event.button() is Qt.MouseButton.LeftButton:
            self.checkbox.toggle()
            event.accept()
            return

        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        if self._icon:
            self._set_hovered(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self._icon:
            self._set_hovered(False)
        super().leaveEvent(event)

    def _set_hovered(self, hovered: bool) -> None:
        self.checkbox.setProperty("hovered", hovered)
        self.checkbox.style().unpolish(self.checkbox)
        self.checkbox.style().polish(self.checkbox)
        self.checkbox.update()

    @property
    def checked(self) -> bool:
        return self.checkbox.isChecked()

    @checked.setter
    def checked(self, state: bool) -> None:
        self.checkbox.setChecked(state)
