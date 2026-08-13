from typing import Any

import pytest

from scfile.app.gui import application


def test_run_initializes_application(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, Any]] = []

    class App:
        def __init__(self, args: list[str]) -> None:
            calls.append(("app", args))

        def setStyle(self, style: str) -> None:
            calls.append(("style", style))

        def exec(self) -> int:
            return 7

    class Window:
        def show(self) -> None:
            calls.append(("show", None))

        def close(self) -> None: ...

    class Timeout:
        def connect(self, callback) -> None:
            calls.append(("connect", callback))

    class Timer:
        def __init__(self) -> None:
            self.timeout = Timeout()

        def start(self, interval: int) -> None:
            calls.append(("timer", interval))

    monkeypatch.setattr(application, "QApplication", App)
    monkeypatch.setattr(application, "MainWindow", Window)
    monkeypatch.setattr(application, "QTimer", Timer)
    monkeypatch.setattr(application, "signal", lambda *args: calls.append(("signal", args)))

    assert application.run() == 7
    assert ("style", "Fusion") in calls
    assert ("timer", 100) in calls
    assert ("show", None) in calls
