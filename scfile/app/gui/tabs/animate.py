from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QStackedWidget, QTabBar, QVBoxLayout, QWidget

from scfile import convert
from scfile.app import files
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.path import PathField
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.tasks.animate import AnimateTask


@dataclass(frozen=True, slots=True)
class PathRule:
    widget: PathField
    suffix: str
    error: str
    required: bool = True


def _valid(rule: PathRule) -> bool:
    value = rule.widget.value.strip()
    path = Path(value)
    return (not rule.required and not value) or (bool(value) and path.is_file() and path.suffix.lower() == rule.suffix)


class AnimationForm(QWidget):
    changed = Signal()
    title = ""
    icon = ""
    source: PathField
    model: PathField

    def __init__(self):
        super().__init__()
        self.rules: list[PathRule] = []
        self.touched: set[PathField] = set()

        self.form_layout = QVBoxLayout(self)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        self.form_layout.addStretch()

    @property
    def source_path(self) -> Path:
        return Path(self.source.value.strip())

    @property
    def model_path(self) -> Path:
        return Path(self.model.value.strip())

    def add_path(
        self,
        label: str,
        caption: str,
        file_filter: str,
        placeholder: str,
        *,
        suffix: str,
        error: str,
        required: bool = True,
    ) -> PathField:
        path = PathField(
            label,
            placeholder=placeholder,
            caption=caption,
            required=required,
            mode="open",
            file_filter=file_filter,
        )
        path.changed.connect(lambda _: self._touch_input(path))
        self.rules.append(PathRule(path, suffix, error, required))
        self.form_layout.insertWidget(self.form_layout.count() - 1, path)
        return path

    def validation_error(self) -> str | None:
        invalid = {rule.widget for rule in self.rules if not _valid(rule)}
        for rule in self.rules:
            rule.widget.invalid = rule.widget in self.touched and rule.widget in invalid

        return next((rule.error for rule in self.rules if rule.widget in invalid), None)

    def _touch_input(self, path: PathField) -> None:
        self.touched.add(path)
        self.changed.emit()


class ArmsForm(AnimationForm):
    title = "mode.animate.fp"
    icon = "hands"

    def __init__(self):
        super().__init__()
        self.source = self.add_path(
            strings.get("label.animate.animation"),
            strings.get("dialog.animate.animation"),
            "MCVD (*.mcvd)",
            "highpoly/animations/wpn_fp_gun.mcvd",
            suffix=".mcvd",
            error="tooltip.animate.invalid.animation",
        )

        self.warnings = WarningsWidget()
        self.form_layout.insertWidget(1, self.warnings)

        self.model = self.add_path(
            strings.get("label.animate.model"),
            strings.get("dialog.animate.model"),
            "MCSB (*.mcsb)",
            "weapons/models/gun/gun.mcsb",
            suffix=".mcsb",
            error="tooltip.animate.invalid.model",
        )
        self.hands = self.add_path(
            strings.get("label.animate.hands"),
            strings.get("dialog.animate.hands"),
            "MCSB (*.mcsb)",
            "highpoly/hands.mcsb",
            suffix=".mcsb",
            error="tooltip.animate.invalid.additional",
            required=False,
        )
        self.changed.connect(self._sync_warnings)

    def create_task(self, output: Path) -> AnimateTask:
        models = [self.model_path]
        if hands := self.hands.value.strip():
            models.append(Path(hands))

        return AnimateTask(
            operation=convert.animate.arms,
            source=self.source_path,
            models=tuple(models),
            output=output,
        )

    def _sync_warnings(self) -> None:
        name = self.source_path.stem.lower()
        is_mcvd = self.source_path.suffix.lower() == ".mcvd"
        warning = is_mcvd and "fp_" not in name and "wpn_" not in name
        messages = (strings.get("warning.animate.not_fp"),) if warning else ()
        self.warnings.set_messages(messages)


class BodyForm(AnimationForm):
    title = "mode.animate.body"
    icon = "body"

    def __init__(self):
        super().__init__()
        self.source = self.add_path(
            strings.get("label.animate.library"),
            strings.get("dialog.animate.library"),
            "MCAL (*.mcal)",
            "highpoly/character/pack.mcal",
            suffix=".mcal",
            error="tooltip.animate.invalid.library",
        )
        self.model = self.add_path(
            strings.get("label.animate.character"),
            strings.get("dialog.animate.character"),
            "MCSB (*.mcsb)",
            "highpoly/character/model.mcsb",
            suffix=".mcsb",
            error="tooltip.animate.invalid.model",
        )

    def create_task(self, output: Path) -> AnimateTask:
        return AnimateTask(
            operation=convert.animate.body,
            source=self.source_path,
            models=(self.model_path,),
            output=output,
        )


class FaceForm(AnimationForm):
    title = "mode.animate.lipsync"
    icon = "face"

    def __init__(self):
        super().__init__()
        self.source = self.add_path(
            strings.get("label.animate.animation"),
            strings.get("dialog.animate.animation"),
            "MCVD (*.mcvd)",
            "highpoly/lipsync/character.mcvd",
            suffix=".mcvd",
            error="tooltip.animate.invalid.animation",
        )
        self.model = self.add_path(
            strings.get("label.animate.head"),
            strings.get("dialog.animate.head"),
            "MCSB (*.mcsb)",
            "stalkerplayer/heads/character.mcsb",
            suffix=".mcsb",
            error="tooltip.animate.invalid.model",
        )

    def create_task(self, output: Path) -> AnimateTask:
        return AnimateTask(
            operation=convert.animate.face,
            source=self.source_path,
            models=(self.model_path,),
            output=output,
        )


type Form = ArmsForm | BodyForm | FaceForm


class AnimateTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self.output_touched = False
        self.forms: tuple[Form, ...] = (ArmsForm(), BodyForm(), FaceForm())
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self._sync()

    @property
    def form(self) -> Form:
        return self.forms[self.stack.currentIndex()]

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.stack = QStackedWidget()
        self._build_modes(layout)
        for form in self.forms:
            form.changed.connect(self._sync)
            self.stack.addWidget(form)
        layout.addWidget(self.stack, 1)

        self.output = PathField(
            strings.get("label.animate.output"),
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.animate.output"),
            mode="save",
            file_filter="GLB (*.glb)",
            default_suffix=".glb",
        )
        self.output.changed.connect(self._output_changed)

        layout.addWidget(self.output)

        self.submit = QPushButton(strings.get("button.animate"))
        self.submit.setFixedHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.clicked.connect(self._start_export)
        layout.addWidget(self.submit)

    def _build_modes(self, layout: QVBoxLayout) -> None:
        self.tabs = QTabBar()
        self.tabs.setStyleSheet(Styles.TABS)
        self.tabs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tabs.setIconSize(QSize(18, 18))

        for form in self.forms:
            icon = QIcon(str(files.resource(f"assets/animate.{form.icon}.png")))
            self.tabs.addTab(icon, strings.get(form.title))

        self.tabs.currentChanged.connect(self._change_form)
        layout.addWidget(self.tabs)

    def _change_form(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self._sync()

    def apply_export_path(self, path: Path) -> None:
        self.settings.export_path = path
        self._sync()

    def _output_changed(self, _: str) -> None:
        self.output_touched = True
        self._sync()

    def _output_invalid(self) -> bool:
        return Path(self.output.value.strip()).suffix.lower() != ".glb"

    def _submit_error(self) -> str | None:
        errors = (
            "tooltip.task.busy" if self.tasks.busy else None,
            self.form.validation_error(),
            "tooltip.animate.invalid.output" if self._output_invalid() else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        source = self.form.source.value.strip()

        if source and not self.output_touched:
            self.output.value = str(self.settings.export_path / Path(source).with_suffix(".glb").name)

        if source:
            self.output.initial_path = str(self.settings.export_path / Path(source).with_suffix(".glb").name)

        self.output.invalid = self.output_touched and self._output_invalid()

        error = self._submit_error()
        self.submit.setEnabled(error is None)
        self.submit.setToolTip(strings.get(error or ""))
        cursor = Qt.CursorShape.PointingHandCursor if error is None else Qt.CursorShape.ForbiddenCursor
        self.submit.setCursor(cursor)

    def _start_export(self) -> None:
        self.tasks.start(self.form.create_task(Path(self.output.value.strip())))
        self._sync()
