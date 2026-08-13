from PySide6.QtCore import QObject, QThread, Signal, Slot

from scfile.app.gui import threads
from scfile.app.tasks import Task, TaskContext, execute


class _TaskWorker(QObject):
    reported = Signal(object)
    completed = Signal(object)
    finished = Signal()

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.context = TaskContext()

    @Slot()
    def run(self) -> None:
        summary = execute(self.task, self.reported.emit, self.context)
        self.completed.emit(summary)
        self.finished.emit()

    def cancel(self) -> None:
        self.context.stop()


class TaskManager(QObject):
    reported = Signal(object)
    completed = Signal(object)
    busy_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._worker: _TaskWorker | None = None
        self._thread: QThread | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def start(self, task: Task) -> bool:
        if self.busy:
            return False

        worker = _TaskWorker(task)

        worker.reported.connect(self.reported.emit)
        worker.completed.connect(self.completed.emit)
        self._worker = worker
        self._thread = threads.job(self, worker, worker.run, worker.finished, self._clear_active_task)
        self.busy_changed.emit(True)
        self._thread.start()
        return True

    def cancel(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    @Slot()
    def _clear_active_task(self) -> None:
        self._worker = None
        self._thread = None
        self.busy_changed.emit(False)
