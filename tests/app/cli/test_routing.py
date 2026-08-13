from pathlib import Path

import pytest

from scfile.app.cli import routing
from scfile.app import cli


@pytest.mark.parametrize(
    ("args", "command"),
    [
        (["convert", "model.mcsb"], "convert"),
        (["--help"], "--help"),
        (["world/map_cache"], "mapcache"),
        (["model.mcsb"], "convert"),
        (["wpn_reload.mcvd", "weapon.mcsb"], "animate"),
    ],
)
def test_resolve(args: list[str], command: str) -> None:
    assert routing.resolve(args)[0] == command


def test_arms() -> None:
    assert not routing._is_arms_sources((Path("animation.mcvd"),))
    assert not routing._is_arms_sources((Path("idle.mcvd"), Path("model.mcsb")))
    assert not routing._is_arms_sources((Path("wpn_idle.mcvd"), Path("model.obj")))
    assert routing._is_arms_sources((Path("wpn_idle.mcvd"), Path("model.mcsb"), Path("hands.mcsb")))


def test_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "resolve", lambda args: args)
    monkeypatch.setattr(cli, "_scfile", lambda **kwargs: None)
    assert cli.run(["convert"]) == 0

    monkeypatch.setattr(cli, "_scfile", lambda **kwargs: 3)
    assert cli.run(["convert"]) == 3
