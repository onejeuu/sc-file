import sys

import click
import pytest

from scfile.app import launcher


def test_main_runs_gui_without_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["scfile"])
    monkeypatch.setattr(launcher, "run_gui", lambda: 7)

    with pytest.raises(SystemExit) as raised:
        launcher.main()

    assert raised.value.code == 7


def test_main_runs_cli_with_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    received: list[list[str]] = []
    monkeypatch.setattr(sys, "argv", ["scfile", "--help"])
    monkeypatch.setattr(launcher, "run_cli", lambda args: received.append(args) or 0)

    with pytest.raises(SystemExit) as raised:
        launcher.main()

    assert raised.value.code == 0
    assert received == [["--help"]]


@pytest.mark.parametrize("error", [click.UsageError("bad"), click.Abort()])
def test_main_translates_cli_errors(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    monkeypatch.setattr(sys, "argv", ["scfile", "convert"])
    monkeypatch.setattr(launcher, "run_cli", lambda _: (_ for _ in ()).throw(error))
    monkeypatch.setattr(launcher.console, "invalid", lambda _: None)
    monkeypatch.setattr(launcher.console, "aborted", lambda _: None)

    with pytest.raises(SystemExit) as raised:
        launcher.main()

    expected = error.exit_code if isinstance(error, click.ClickException) else 130
    assert raised.value.code == expected
