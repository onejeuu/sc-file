from typing import Any

from click.testing import CliRunner

from scfile.app import updates
from scfile.app.cli import _scfile, callbacks
from scfile.app.enums import UpdateStatus


def test_version_callback(monkeypatch) -> None:
    calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(callbacks.console, "version", lambda *args: calls.append(args))

    result = CliRunner().invoke(_scfile, ["--version"])

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0][0]


def test_updates_callback(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        callbacks.updates,
        "check",
        lambda _: updates.UpdateCheck(UpdateStatus.AVAILABLE, "", "https://example.invalid/release"),
    )
    monkeypatch.setattr(callbacks.console, "info", calls.append)

    result = CliRunner().invoke(_scfile, ["--updates"])

    assert result.exit_code == 0
    assert len(calls) == 1


def test_updates_callback_reports_up_to_date(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        callbacks.updates,
        "check",
        lambda _: updates.UpdateCheck(UpdateStatus.UPTODATE, "", ""),
    )
    monkeypatch.setattr(callbacks.console, "info", calls.append)

    result = CliRunner().invoke(_scfile, ["--updates"])

    assert result.exit_code == 0
    assert len(calls) == 1


def test_updates_callback_reports_error_and_hint(monkeypatch) -> None:
    errors: list[str] = []
    hints: list[str] = []
    monkeypatch.setattr(
        callbacks.updates,
        "check",
        lambda _: updates.UpdateCheck(UpdateStatus.ERROR, "network", "https://example.invalid"),
    )
    monkeypatch.setattr(callbacks.console, "error", errors.append)
    monkeypatch.setattr(callbacks.console, "hint", hints.append)

    result = CliRunner().invoke(_scfile, ["--updates"])

    assert result.exit_code == 0
    assert len(errors) == 1
    assert len(hints) == 1
