import json
from collections.abc import Callable
from pathlib import Path
from shutil import copyfile
from typing import Any

import pytest
from click.testing import CliRunner

from scfile.app.cli import scfile
from scfile.app.cli.cmd import animate as animate_module
from scfile.app.cli.cmd import convert as convert_module
from scfile.app.cli.cmd import mapcache as mapcache_module
from scfile.app.cli.cmd import maptiles as maptiles_module
from scfile.app.enums import OutputLayout, TaskKind
from scfile.content import ModelContent
from scfile.convert.regions import Region
from scfile.enums import FileFormat, OnConflict


MAP_TILE = Path(__file__).parents[2] / "assets/formats/textures/source/texture_rgba.ol"


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
    assert task.layout is OutputLayout.ROOTED
    assert task.workers == 3
    assert task.filters == (FileFormat.MIC.suffix,)
    assert task.options.targets[ModelContent] is FileFormat.GLB
    assert task.options.skeleton
    assert task.options.animation
    assert task.options.on_conflict is OnConflict.RENAME


@pytest.mark.parametrize("layout", OutputLayout)
def test_convert_layout(tmp_path: Path, layout: OutputLayout) -> None:
    source = tmp_path / "source"
    source.mkdir()

    result = CliRunner().invoke(scfile, ["convert", str(source), "--layout", layout.value])

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
    assert tasks[1].options.preserve_clips


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
) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    output = tmp_path / "regions"
    tasks = command_runner(mapcache_module, TaskKind.MAPCACHE, False)
    result = CliRunner().invoke(
        scfile,
        ["mapcache", str(source), "-O", str(output), "--no-biomes", "--no-backup", "-W", "2", "--verbose"],
    )

    assert result.exit_code == 0
    task = tasks[0]
    assert task.source == source
    assert task.output == output
    assert task.workers == 2
    assert not task.options.biomes
    assert not task.options.backup_regions


def test_maptiles_game(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    game = tmp_path / "game"
    base = game / "modassets/assets/pda/map"
    localized = game / "modassets/assets/_localized/ru/pda/map_bar_save"
    patch = game / "bin_ru/patchassets/assets/pda/map"
    for folder in (base, localized, patch):
        folder.mkdir(parents=True)
        copyfile(MAP_TILE, folder / "r.0.0.ol")

    output = tmp_path / "map.jpg"
    tasks = command_runner(maptiles_module, TaskKind.MAPTILES, False)

    result = CliRunner().invoke(
        scfile,
        ["maptiles", str(game), "map", str(output), "--region", "ru"],
    )

    assert result.exit_code == 0
    assert tasks[0].tiles == {Region(0, 0): patch / "r.0.0.ol"}

    result = CliRunner().invoke(
        scfile,
        ["maptiles", str(game), "map_bar_save", str(output), "--region", "ru"],
    )

    assert result.exit_code == 0
    assert tasks[1].tiles == {Region(0, 0): localized / "r.0.0.ol"}

    result = CliRunner().invoke(
        scfile,
        ["maptiles", str(game), "map", str(output), "--region", "missing"],
    )

    assert result.exit_code != 0


def test_mapcache_failure(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    command_runner(mapcache_module, TaskKind.MAPCACHE, True)
    result = CliRunner().invoke(scfile, ["mapcache", str(source)])

    assert result.exit_code == 1


@pytest.mark.parametrize(
    ("name", "options", "save"),
    (
        ("map.jpg", (), {"format": "JPEG", "quality": 92}),
        ("map.png", (), {"format": "PNG", "compress_level": 6}),
        ("map.png", ("--png-compression", "9"), {"format": "PNG", "compress_level": 9}),
        ("map.jpeg", ("--jpeg-quality", "95"), {"format": "JPEG", "quality": 95}),
    ),
)
def test_maptiles(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
    name: str,
    options: tuple[str, ...],
    save: dict[str, int | str],
) -> None:
    source = tmp_path / "tiles"
    source.mkdir()
    tile = source / "r.0.0.ol"
    copyfile(MAP_TILE, tile)
    output = tmp_path / name
    tasks = command_runner(maptiles_module, TaskKind.MAPTILES, False)

    result = CliRunner().invoke(scfile, ["maptiles", str(source), str(output), *options])

    assert result.exit_code == 0
    task = tasks[0]
    assert task.tiles == {Region(0, 0): tile}
    assert task.output == output
    assert task.save == save


@pytest.mark.parametrize(
    ("name", "options"),
    (
        ("map.jpg", ("--png-compression", "6")),
        ("map.png", ("--jpeg-quality", "92")),
        ("map.webp", ()),
    ),
)
def test_maptiles_validation(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
    name: str,
    options: tuple[str, ...],
) -> None:
    source = tmp_path / "tiles"
    source.mkdir()
    copyfile(MAP_TILE, source / "r.0.0.ol")
    tasks = command_runner(maptiles_module, TaskKind.MAPTILES, False)
    result = CliRunner().invoke(scfile, ["maptiles", str(source), str(tmp_path / name), *options])

    assert result.exit_code != 0
    assert not tasks


def test_maptiles_empty(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "tiles"
    source.mkdir()
    tasks = command_runner(maptiles_module, TaskKind.MAPTILES, False)

    result = CliRunner().invoke(scfile, ["maptiles", str(source), str(tmp_path / "map.jpg")])

    assert result.exit_code != 0
    assert not tasks


def test_maptiles_failure(
    tmp_path: Path,
    command_runner: Callable[[Any, TaskKind, bool], list[Any]],
) -> None:
    source = tmp_path / "tiles"
    source.mkdir()
    copyfile(MAP_TILE, source / "r.0.0.ol")
    command_runner(maptiles_module, TaskKind.MAPTILES, True)

    result = CliRunner().invoke(scfile, ["maptiles", str(source), str(tmp_path / "map.jpg")])

    assert result.exit_code == 1


def test_convert_run(tmp_path: Path) -> None:
    source = Path(__file__).parents[2] / "assets/formats/document/source/document.nbt"
    output = tmp_path / "output"

    result = CliRunner().invoke(scfile, ["convert", str(source), "-O", str(output), "-W", "1"])

    assert result.exit_code == 0
    target = output / "document.json"
    assert target.exists()
    assert isinstance(json.loads(target.read_text(encoding="utf-8")), dict)
