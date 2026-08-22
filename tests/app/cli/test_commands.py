from collections.abc import Callable
from pathlib import Path
from typing import Any
import json

from click.testing import CliRunner

from scfile.app.cli import scfile
from scfile.app.cli.cmd import animate as animate_module
from scfile.app.cli.cmd import convert as convert_module
from scfile.app.cli.cmd import mapcache as mapcache_module
from scfile.app.enums import OutputLayout, TaskKind
from scfile.enums import FileFormat, OnConflict
from scfile.structures.content import ModelContent


def test_convert(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    output = tmp_path / "output"
    tasks = command_runner(convert_module, TaskKind.CONVERT, False)

    result = CliRunner().invoke(
        scfile,
        [
            "convert",
            str(source),
            "-O",
            str(output),
            "-I",
            "mic",
            "-F",
            "glb",
            "--skeleton",
            "--animation",
            "--on-conflict",
            "rename",
            "-W",
            "3",
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    task = tasks[0]
    assert task.sources == (source,)
    assert task.output == output
    assert task.layout is OutputLayout.RELATIVE
    assert task.workers == 3
    assert task.filters == (FileFormat.MIC.suffix,)
    assert task.options.targets[ModelContent] is FileFormat.GLB
    assert task.options.skeleton
    assert task.options.animation
    assert task.options.on_conflict is OnConflict.RENAME


def test_convert_layout(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    result = CliRunner().invoke(scfile, ["convert", str(source), "--layout", "relative"])

    assert result.exit_code == 0


def test_convert_failure(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    command_runner(convert_module, TaskKind.CONVERT, True)

    result = CliRunner().invoke(scfile, ["convert", str(source)])

    assert result.exit_code == 1


def test_convert_features(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
    monkeypatch,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    command_runner(convert_module, TaskKind.CONVERT, False)
    warnings: list[str] = []
    monkeypatch.setattr(convert_module, "warn", warnings.append)

    result = CliRunner().invoke(scfile, ["convert", str(source), "-F", "obj", "--skeleton"])

    assert result.exit_code == 0
    assert len(warnings) == 1


def test_arms(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    animation = tmp_path / "animation.mcvd"
    model = tmp_path / "model.mcsb"
    hands = tmp_path / "hands.mcsb"
    for path in (animation, model, hands):
        path.touch()
    tasks = command_runner(animate_module, TaskKind.ANIMATE, False)

    result = CliRunner().invoke(
        scfile,
        ["animate", "arms", str(animation), str(model), str(hands), "-O", str(tmp_path)],
    )

    assert result.exit_code == 0
    task = tasks[0]
    assert task.operation is animate_module.convert.animate.arms
    assert task.source == animation
    assert task.models == (model, hands)
    assert task.output == tmp_path / "animation.glb"


def test_animate(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "source"
    model = tmp_path / "model"
    source.touch()
    model.touch()
    tasks = command_runner(animate_module, TaskKind.ANIMATE, False)
    runner = CliRunner()

    face = runner.invoke(scfile, ["animate", "face", str(source), str(model), "-O", str(tmp_path)])
    body = runner.invoke(scfile, ["animate", "body", str(source), str(model), "-O", str(tmp_path), "--raw"])

    assert face.exit_code == 0
    assert body.exit_code == 0
    assert tasks[0].operation is animate_module.convert.animate.face
    assert tasks[1].operation is animate_module.convert.animate.body
    assert tasks[1].options.raw_clips


def test_animate_failure(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "source"
    model = tmp_path / "model"
    source.touch()
    model.touch()
    command_runner(animate_module, TaskKind.ANIMATE, True)

    result = CliRunner().invoke(scfile, ["animate", "body", str(source), str(model)])

    assert result.exit_code == 1


def test_mapcache(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
    monkeypatch,
) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    output = tmp_path / "regions"
    tasks = command_runner(mapcache_module, TaskKind.MAPCACHE, False)
    monkeypatch.setattr(mapcache_module, "warn", lambda _: None)

    result = CliRunner().invoke(
        scfile,
        ["mapcache", str(source), "-O", str(output), "--raw", "-W", "2", "--verbose"],
    )

    assert result.exit_code == 0
    task = tasks[0]
    assert task.source == source
    assert task.output == output
    assert task.workers == 2
    assert task.options.raw_blocks


def test_mapcache_failure(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
    monkeypatch,
) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    command_runner(mapcache_module, TaskKind.MAPCACHE, True)
    monkeypatch.setattr(mapcache_module, "warn", lambda _: None)

    result = CliRunner().invoke(scfile, ["mapcache", str(source)])

    assert result.exit_code == 1


def test_convert_run(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    output = tmp_path / "output"

    result = CliRunner().invoke(scfile, ["convert", str(source), "-O", str(output), "-W", "1"])

    assert result.exit_code == 0
    target = output / "document.json"
    assert target.exists()
    assert isinstance(json.loads(target.read_text(encoding="utf-8")), dict)
