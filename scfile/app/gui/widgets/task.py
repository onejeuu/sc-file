from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy, QWidget

from scfile.app.gui.shared import strings
from scfile.app.gui.shared.styles import Colors, Styles
from scfile.app.gui.workers import TaskManager
from scfile.app.tasks import PROGRESS_THRESHOLD, Progress, Started, Summary, TaskKind


class TaskWidget(QWidget):
    """Compact status and progress for the active application task."""

    def __init__(self, tasks: TaskManager):
        super().__init__()
        self._tasks = tasks

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        self.status = QLabel()
        self.status.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.progress = QProgressBar()
        self.progress.setMinimumWidth(220)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar {{ background: {Colors.CARD}; border: 1px solid {Colors.BORDER}; "
            f"border-radius: 3px; }} "
            f"QProgressBar::chunk {{ background: {Colors.ACCENT}; }}"
        )
        self.progress_text = QLabel()
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.cancel = QPushButton(strings.get("button.task.cancel"))
        self.cancel.setStyleSheet(Styles.BUTTON)
        self.cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel.clicked.connect(self._cancel)

        self.dismiss = QPushButton("×")
        self.dismiss.setFixedWidth(28)
        self.dismiss.setStyleSheet(Styles.BUTTON)
        self.dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dismiss.setToolTip(strings.get("tooltip.task.dismiss"))
        self.dismiss.clicked.connect(self.hide)
        self.dismiss.hide()

        layout.addWidget(self.status, 1)
        layout.addWidget(self.progress)
        layout.addWidget(self.progress_text)
        layout.addWidget(self.cancel)
        layout.addWidget(self.dismiss)

        tasks.busy_changed.connect(self._on_busy_changed)
        tasks.reported.connect(self._on_event)
        tasks.completed.connect(self._on_completed)
        self.hide()

    def _on_busy_changed(self, busy: bool) -> None:
        if not busy:
            return

        self.status.setText(strings.get("task.running"))
        self.status.setStyleSheet(f"color: {Colors.TEXT};")
        self.progress.hide()
        self.progress_text.hide()
        self.cancel.setText(strings.get("button.task.cancel"))
        self.cancel.setEnabled(True)
        self.cancel.show()
        self.dismiss.hide()
        self.show()

    def _on_event(self, event: object) -> None:
        if isinstance(event, Started):
            self._on_started(event)
            return

        if not isinstance(event, Progress) or event.total is None:
            return

        if event.total < PROGRESS_THRESHOLD:
            self.progress.hide()
            self.progress_text.hide()
            return

        self.progress.setRange(0, event.total)
        self.progress.setValue(event.completed)
        percent = event.completed / event.total
        self.progress_text.setText(f"{event.completed:,}/{event.total:,} · {percent:.0%}")
        self.progress.show()
        self.progress_text.show()

    def _on_started(self, event: Started) -> None:
        keys = {
            TaskKind.CONVERT: "task.running.convert",
            TaskKind.MAPCACHE: "task.running.mapcache",
            TaskKind.ANIMATE: "task.running.animate",
        }
        text = strings.get(keys[event.kind]).format(total=f"{event.total:,}")
        self._set_status(text, event.kind, event.output, Colors.TEXT)

    def _on_completed(self, summary: object) -> None:
        if not isinstance(summary, Summary):
            return

        self.progress.hide()
        self.progress_text.hide()
        self.cancel.hide()
        self.dismiss.show()
        values = {
            "completed": f"{summary.completed:,}",
            "total": f"{summary.total:,}",
            "converted": f"{summary.succeeded:,}",
            "written": f"{summary.written:,}",
            "skipped": f"{summary.skipped:,}",
            "failed": f"{summary.failed:,}",
        }

        if summary.cancelled:
            keys = {
                TaskKind.CONVERT: "task.cancelled.convert",
                TaskKind.MAPCACHE: "task.cancelled.mapcache",
                TaskKind.ANIMATE: "task.cancelled.animate",
            }
            key = keys[summary.kind]
            color = Colors.WARNING
        else:
            if summary.kind is TaskKind.CONVERT:
                if not summary.succeeded:
                    key = "task.result.convert.empty"
                elif summary.failed:
                    key = "task.result.convert"
                else:
                    key = "task.result.convert.simple"
            else:
                keys = {
                    TaskKind.MAPCACHE: "task.result.mapcache",
                    TaskKind.ANIMATE: "task.result.animate",
                }
                key = keys[summary.kind]
            color = Colors.WARNING if summary.failed else Colors.SUCCESS

        text = strings.get(key).format(**values)
        if summary.skipped:
            text = f'{text} · {strings.get("task.skipped").format(skipped=values["skipped"])}'
        if summary.failed:
            text = f'{text} · {strings.get("task.errors").format(failed=values["failed"])}'
        self._set_status(text, summary.kind, summary.output, color)
        self.show()

    def _cancel(self) -> None:
        self._tasks.cancel()
        self.cancel.setText(strings.get("button.task.cancelling"))
        self.cancel.setEnabled(False)

    def _set_status(
        self,
        text: str,
        kind: TaskKind,
        output: Path | None,
        color: Colors,
    ) -> None:
        if output is None and kind is TaskKind.CONVERT:
            destination = strings.get("task.output.alongside")
        else:
            destination = str(output)

        message = f'{text} · {strings.get("task.output").format(output=destination)}'
        self.status.setText(message)
        self.status.setToolTip(message)
        self.status.setStyleSheet(f"color: {color};")
