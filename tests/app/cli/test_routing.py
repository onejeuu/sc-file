from pathlib import Path

import pytest

from scfile.app.cli import routing
from scfile.app import cli
from scfile.app.enums import AnimateCommand


@pytest.mark.parametrize(
    ("args", "command"),
    [
        (["convert", "model.mcsb"], "convert"),
        (["--help"], "--help"),
        (["world/map_cache"], "mapcache"),
        (["model.mcsb"], "convert"),
        (["library.mcal", "model.mcsb"], "animate"),
        (["wpn_reload.mcvd", "weapon.mcsb"], "animate"),
        (["face.mcvd", "head.mcsb"], "animate"),
    ],
)
def test_resolve(args: list[str], command: str) -> None:
    assert routing.resolve(args)[0] == command


def test_animation() -> None:
    assert routing._animation((Path("library.mcal"), Path("model.mcsb"))) is AnimateCommand.BODY
    assert routing._animation((Path("wpn_idle.mcvd"), Path("model.mcsb"))) is AnimateCommand.ARMS
    assert routing._animation((Path("fp_idle.mcvd"), Path("model.mcsb"), Path("hands.mcsb"))) is AnimateCommand.ARMS
    assert routing._animation((Path("idle.mcvd"), Path("model.mcsb"))) is AnimateCommand.FACE
    assert routing._animation((Path("library.mcal"), Path("model.mcsb"), Path("hands.mcsb"))) is None
    assert routing._animation((Path("wpn_idle.mcvd"), Path("model.obj"))) is None


def test_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "resolve", lambda args: args)
    monkeypatch.setattr(cli, "scfile", lambda **kwargs: None)
    assert cli.run(["convert"]) == 0

    monkeypatch.setattr(cli, "scfile", lambda **kwargs: 3)
    assert cli.run(["convert"]) == 3
