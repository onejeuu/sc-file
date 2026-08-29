from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from scfile.app.gui import strings
from scfile.app.gui.styles import Styles
from scfile.app.tasks.mapmerge import MapImageFormat
from scfile.convert import mapmerge


class ImageEncodingWidget(QWidget):
    changed = Signal(object)

    def __init__(self):
        super().__init__()
        self._values = {
            MapImageFormat.JPEG: mapmerge.JPEG_QUALITY,
            MapImageFormat.PNG: mapmerge.PNG_COMPRESSION,
        }
        self._syncing = False
        self._build_ui()

        self.format = MapImageFormat(mapmerge.DEFAULT_SAVE["format"])

    @property
    def format(self) -> MapImageFormat:
        return self._format

    @format.setter
    def format(self, value: MapImageFormat) -> None:
        self._format = value
        self._buttons[value].setChecked(True)
        self._refresh()

    @property
    def jpeg_quality(self) -> int:
        return self._values[MapImageFormat.JPEG]

    @property
    def png_compression(self) -> int:
        return self._values[MapImageFormat.PNG]

    @property
    def save(self) -> mapmerge.SaveOptions:
        return self.format.save(self._values[self.format])

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        toggle = QWidget()
        toggle.setStyleSheet(Styles.TOGGLE_GROUP)
        toggle_layout = QHBoxLayout(toggle)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)

        self.buttons = QButtonGroup(self)
        self.buttons.setExclusive(True)
        self._buttons: dict[MapImageFormat, QPushButton] = {}
        for image_format in MapImageFormat:
            button = QPushButton(image_format.value)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            button.setProperty("image_format", image_format.value)
            self.buttons.addButton(button)
            self._buttons[image_format] = button
            toggle_layout.addWidget(button)
        self.buttons.buttonClicked.connect(self._selected)

        self.label = QLabel()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setStyleSheet(Styles.SLIDER)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.spin = QSpinBox()
        self.spin.setStyleSheet(Styles.SPIN)
        self.spin.setFixedWidth(60)

        self.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.setValue)
        self.spin.valueChanged.connect(self._store)

        layout.addWidget(toggle)
        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spin)

    def _selected(self, button: QPushButton) -> None:
        image_format = MapImageFormat(button.property("image_format"))
        self.format = image_format
        self.changed.emit(image_format)

    def _refresh(self) -> None:
        self._syncing = True
        try:
            match self.format:
                case MapImageFormat.JPEG:
                    self.label.setText(strings.get("label.mapmerge.quality"))
                    bounds = (0, 100)
                case MapImageFormat.PNG:
                    self.label.setText(strings.get("label.mapmerge.compression"))
                    bounds = (0, 9)

            self.slider.setRange(*bounds)
            self.spin.setRange(*bounds)
            self.spin.setValue(self._values[self.format])
            self.slider.setValue(self._values[self.format])
        finally:
            self._syncing = False

    def _store(self, value: int) -> None:
        if not self._syncing:
            self._values[self.format] = value
