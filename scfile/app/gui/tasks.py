from PySide6.QtCore import QObject, QThread, Signal, Slot

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

        thread = QThread(self)
        worker = _TaskWorker(task)
        worker.moveToThread(thread)

        worker.reported.connect(self.reported.emit)
        worker.completed.connect(self.completed.emit)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._clear_active_task)
        thread.finished.connect(thread.deleteLater)
        thread.started.connect(worker.run)

        self._worker = worker
        self._thread = thread
        self.busy_changed.emit(True)
        thread.start()
        return True

    def cancel(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    @Slot()
    def _clear_active_task(self) -> None:
        self._worker = None
        self._thread = None
        self.busy_changed.emit(False)
