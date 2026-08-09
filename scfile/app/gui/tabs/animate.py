from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from scfile import convert
from scfile.app.gui.shared import strings
from scfile.app.gui.shared.styles import Colors, Styles
from scfile.app.gui.widgets.path import PathInputWidget
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.gui.workers import TaskManager
from scfile.app.tasks.animation import Job


def _required_label(label: str) -> str:
    return f'{label} <span style="color: {Colors.ERROR}">*</span>'


class AnimationForm(QWidget):
    changed = Signal()
    source: PathInputWidget
    model: PathInputWidget

    def __init__(
        self,
        source_suffix: str,
        source_error: str,
    ):
        super().__init__()
        self._source_suffix = source_suffix
        self._source_error = source_error
        self._paths: list[PathInputWidget] = []
        self._touched: set[PathInputWidget] = set()

        self.form_layout = QVBoxLayout(self)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        self.form_layout.addStretch()

    def _add_path(
        self,
        label: str,
        caption: str,
        file_filter: str,
        placeholder: str,
        required: bool = True,
    ) -> PathInputWidget:
        title = QLabel(_required_label(label) if required else label)
        title.setStyleSheet(Styles.LABEL)
        path = PathInputWidget(
            placeholder=placeholder,
            caption=caption,
            mode="open",
            file_filter=file_filter,
        )
        path.changed.connect(lambda _: self._notify_changed(path))
        self._paths.append(path)
        self.form_layout.insertWidget(self.form_layout.count() - 1, title)
        self.form_layout.insertWidget(self.form_layout.count() - 1, path)
        return path

    def _notify_changed(self, path: PathInputWidget) -> None:
        self._touched.add(path)
        self.changed.emit()

    @staticmethod
    def _valid_file(value: str, suffix: str) -> bool:
        path = Path(value.strip())
        return bool(value.strip()) and path.is_file() and path.suffix.lower() == suffix

    @property
    def source_path(self) -> Path:
        return Path(self.source.text().strip())

    @property
    def model_path(self) -> Path:
        return Path(self.model.text().strip())

    def invalid_paths(self) -> tuple[PathInputWidget, ...]:
        paths = []
        if not self._valid_file(self.source.text(), self._source_suffix):
            paths.append(self.source)
        if not self._valid_file(self.model.text(), ".mcsb"):
            paths.append(self.model)
        return tuple(paths)

    def _set_invalid_paths(self, invalid: tuple[PathInputWidget, ...]) -> None:
        for path in self._paths:
            path.invalid = path in self._touched and path in invalid

    def validation_error(self) -> str | None:
        invalid = self.invalid_paths()
        self._set_invalid_paths(invalid)
        if self.source in invalid:
            return self._source_error
        if self.model in invalid:
            return "tooltip.animate.invalid.model"
        return None


class BodyForm(AnimationForm):
    def __init__(self):
        super().__init__(
            source_suffix=".mcal",
            source_error="tooltip.animate.invalid.library",
        )
        self.source = self._add_path(
            strings.get("label.animate.library"),
            strings.get("dialog.animate.library"),
            "MCAL (*.mcal)",
            "highpoly/character/pack.mcal",
        )
        self.model = self._add_path(
            strings.get("label.animate.character"),
            strings.get("dialog.animate.character"),
            "MCSB (*.mcsb)",
            "highpoly/character/model.mcsb",
        )

    def create_task(self, output: Path) -> Job:
        return Job(
            operation=convert.animate.body,
            source=self.source_path,
            models=(self.model_path,),
            output=output,
        )


class ArmsForm(AnimationForm):
    def __init__(self):
        super().__init__(
            source_suffix=".mcvd",
            source_error="tooltip.animate.invalid.animation",
        )
        self.source = self._add_path(
            strings.get("label.animate.animation"),
            strings.get("dialog.animate.animation"),
            "MCVD (*.mcvd)",
            "highpoly/animations/wpn_fp_gun.mcvd",
        )
        self.model = self._add_path(
            strings.get("label.animate.model"),
            strings.get("dialog.animate.model"),
            "MCSB (*.mcsb)",
            "weapons/models/gun/gun.mcsb",
        )
        self.warnings = WarningsWidget()
        self.warnings.add_rule(self._warn_not_fp_animation)
        self.form_layout.insertWidget(2, self.warnings)
        self.changed.connect(self.warnings.update_state)

        self.additional_model = self._add_path(
            strings.get("label.animate.additional"),
            strings.get("dialog.animate.additional"),
            "MCSB (*.mcsb)",
            "highpoly/hands.mcsb",
            required=False,
        )

    def _warn_not_fp_animation(self) -> str | None:
        animation = self.source_path
        name = animation.stem.lower()
        if animation.suffix.lower() == ".mcvd" and "fp_" not in name and "wpn_" not in name:
            return strings.get("warning.animate.not_fp")
        return None

    def invalid_paths(self) -> tuple[PathInputWidget, ...]:
        paths = list(super().invalid_paths())
        additional = self.additional_model.text().strip()
        if additional and not self._valid_file(additional, ".mcsb"):
            paths.append(self.additional_model)
        return tuple(paths)

    def validation_error(self) -> str | None:
        invalid = self.invalid_paths()
        self._set_invalid_paths(invalid)
        if self.source in invalid:
            return self._source_error
        if self.model in invalid:
            return "tooltip.animate.invalid.model"
        if self.additional_model in invalid:
            return "tooltip.animate.invalid.additional"
        return None

    def create_task(self, output: Path) -> Job:
        models = [self.model_path]
        if additional := self.additional_model.text().strip():
            models.append(Path(additional))

        return Job(
            operation=convert.animate.arms,
            source=self.source_path,
            models=tuple(models),
            output=output,
        )


class FaceForm(AnimationForm):
    def __init__(self):
        super().__init__(
            source_suffix=".mcvd",
            source_error="tooltip.animate.invalid.animation",
        )
        self.source = self._add_path(
            strings.get("label.animate.animation"),
            strings.get("dialog.animate.animation"),
            "MCVD (*.mcvd)",
            "highpoly/lipsync/character.mcvd",
        )
        self.model = self._add_path(
            strings.get("label.animate.head"),
            strings.get("dialog.animate.head"),
            "MCSB (*.mcsb)",
            "stalkerplayer/heads/character.mcsb",
        )

    def create_task(self, output: Path) -> Job:
        return Job(
            operation=convert.animate.face,
            source=self.source_path,
            models=(self.model_path,),
            output=output,
        )


class AnimateTab(QWidget):
    def __init__(self, tasks: TaskManager):
        super().__init__()
        self.tasks = tasks
        self._active = False
        self._output_touched = False
        self.tasks.busy_changed.connect(self._sync_ui)
        self.tasks.completed.connect(self._on_finish)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.forms = QStackedWidget()
        self._forms: tuple[BodyForm | ArmsForm | FaceForm, ...] = (
            ArmsForm(),
            BodyForm(),
            FaceForm(),
        )

        self._add_modes(layout)
        for form in self._forms:
            form.changed.connect(self._sync_ui)
            self.forms.addWidget(form)
        layout.addWidget(self.forms, 1)

        output_label = QLabel(strings.get("label.animate.output"))
        output_label.setText(_required_label(strings.get("label.animate.output")))
        output_label.setStyleSheet(Styles.LABEL)
        self.output = PathInputWidget(
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.animate.output"),
            mode="save",
            file_filter="GLB (*.glb)",
            default_suffix=".glb",
        )
        self.output.changed.connect(self._output_changed)

        layout.addWidget(output_label)
        layout.addWidget(self.output)

        self.export = QPushButton(strings.get("button.animate"))
        self.export.setFixedHeight(50)
        self.export.setStyleSheet(Styles.BUTTON_ACCENT)
        self.export.clicked.connect(self._animate)
        layout.addWidget(self.export)

        self._sync_ui()

    def _add_modes(self, layout: QVBoxLayout) -> None:
        widget = QWidget()
        widget.setStyleSheet(Styles.TOGGLE_GROUP)
        modes = QHBoxLayout(widget)
        modes.setContentsMargins(0, 0, 0, 0)
        modes.setSpacing(0)

        self.mode = QButtonGroup(self)
        self.mode.setExclusive(True)
        # TODO: autosync with forms order
        titles = (
            "mode.animate.fp",
            "mode.animate.body",
            "mode.animate.lipsync",
        )
        buttons = []
        for index, title in enumerate(titles):
            button = QPushButton(strings.get(title))
            button.setCheckable(True)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            modes.addWidget(button)
            self.mode.addButton(button, index)
            buttons.append(button)

        buttons[0].setChecked(True)
        self.mode.idClicked.connect(self._change_form)
        layout.addWidget(widget)

    def _change_form(self, index: int) -> None:
        self.forms.setCurrentIndex(index)
        self._sync_ui()

    def _output_changed(self, _: str) -> None:
        self._output_touched = True
        self._sync_ui()

    @property
    def _form(self) -> BodyForm | ArmsForm | FaceForm:
        return self._forms[self.forms.currentIndex()]

    def _sync_ui(self) -> None:
        form = self._form
        source = form.source.text().strip()
        output = self.output.text().strip()

        if source:
            self.output.initial_path = Path(source).with_suffix(".glb").name

        error = form.validation_error()
        output_invalid = Path(output).suffix.lower() != ".glb"
        self.output.invalid = self._output_touched and output_invalid
        if error is None and output_invalid:
            error = "tooltip.animate.invalid.output"

        ready = error is None and not self.tasks.busy
        if self.tasks.busy:
            error = "tooltip.task.busy"
        self.export.setEnabled(ready)
        self.export.setToolTip(strings.get(error or ""))
        self.export.setCursor(Qt.CursorShape.PointingHandCursor if ready else Qt.CursorShape.ForbiddenCursor)

    def _animate(self) -> None:
        self._active = True
        task = self._form.create_task(Path(self.output.text().strip()))
        if not self.tasks.start(task):
            self._active = False
        self._sync_ui()

    def _on_finish(self, _: object) -> None:
        if not self._active:
            return
        self._active = False
        self._sync_ui()
