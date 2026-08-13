from typing import Any, cast

import pytest
from click.testing import CliRunner

from scfile.app import updates
from scfile.app.cli import _scfile, callbacks
from scfile.app.enums import UpdateStatus


def test_version(monkeypatch) -> None:
    calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(callbacks.console, "version", lambda *args: calls.append(args))

    result = CliRunner().invoke(_scfile, ["--version"])

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0][0]


def test_updates(monkeypatch) -> None:
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


def test_updates_current(monkeypatch) -> None:
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


def test_updates_error(monkeypatch) -> None:
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


def test_updates_error_plain(monkeypatch) -> None:
    errors: list[str] = []
    monkeypatch.setattr(
        callbacks.updates,
        "check",
        lambda _: updates.UpdateCheck(UpdateStatus.ERROR, "network", ""),
    )
    monkeypatch.setattr(callbacks.console, "error", errors.append)
    monkeypatch.setattr(callbacks.console, "hint", lambda _: pytest.fail("unexpected hint"))

    result = CliRunner().invoke(_scfile, ["--updates"])

    assert result.exit_code == 0
    assert len(errors) == 1


def test_updates_unknown(monkeypatch) -> None:
    monkeypatch.setattr(callbacks.updates, "check", lambda _: updates.UpdateCheck(cast(UpdateStatus, object()), "", ""))

    result = CliRunner().invoke(_scfile, ["--updates"])

    assert result.exit_code == 0
