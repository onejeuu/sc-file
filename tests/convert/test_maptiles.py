from pathlib import Path
from shutil import copyfile

import pytest
from PIL import Image

from scfile import exceptions
from scfile.convert import maptiles
from scfile.enums import OnConflict
from scfile.options import Options


SOURCE = Path(__file__).parents[1] / "assets/formats/textures/source/texture_rgba.ol"


def _tile(folder: Path, x: int, z: int) -> Path:
    path = folder / f"r.{x}.{z}.ol"
    copyfile(SOURCE, path)
    return path


def test_scan(tmp_path: Path) -> None:
    expected = _tile(tmp_path, -1, 2)
    (tmp_path / "r.0.0.ol").write_bytes(b"garbage")
    copyfile(SOURCE, tmp_path / "texture.ol")

    assert maptiles.scan(tmp_path) == {maptiles.Region(-1, 2): expected}


def test_collect(tmp_path: Path) -> None:
    base = tmp_path / "base"
    patch = tmp_path / "patch"
    base.mkdir()
    patch.mkdir()

    original = _tile(base, 0, 0)
    unchanged = _tile(base, 1, 0)
    replacement = _tile(patch, 0, 0)
    (patch / "r.1.0.ol").write_bytes(b"garbage")

    assert maptiles.collect((base, patch)) == {
        maptiles.Region(0, 0): replacement,
        maptiles.Region(1, 0): unchanged,
    }
    assert original != replacement


def test_merge(tmp_path: Path) -> None:
    _tile(tmp_path, -1, 1)
    _tile(tmp_path, 0, 1)
    output = tmp_path / "output/map.jpg"

    result = maptiles.assemble(tmp_path, output)

    assert result == maptiles.AssembleResult(output, 2)
    with Image.open(output) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert image.size == (1344, 504)


def test_measure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = _tile(tmp_path, 0, 0)
    second = _tile(tmp_path, 1, 1)
    tiles = maptiles.scan(tmp_path)
    monkeypatch.setattr(maptiles, "_size", lambda *args: maptiles.Size(4, 3))
    monkeypatch.setattr(maptiles, "_decode", lambda *args: pytest.fail("decoded tile pixels"))

    assert tiles == {maptiles.Region(0, 0): first, maptiles.Region(1, 1): second}
    assert maptiles.measure(tiles) == maptiles.Size(8, 6)


def test_progress(tmp_path: Path) -> None:
    paths = [_tile(tmp_path, 0, 0), _tile(tmp_path, 1, 0)]
    completed: list[Path] = []

    maptiles.assemble(tmp_path, tmp_path / "map.jpg", progress=completed.append)

    assert completed == paths


def test_empty(tmp_path: Path) -> None:
    with pytest.raises(exceptions.ConversionError, match="No map tiles found"):
        maptiles.assemble(tmp_path, tmp_path / "map.jpg")


def test_output_format(tmp_path: Path) -> None:
    _tile(tmp_path, 0, 0)
    output = tmp_path / "map.png"

    maptiles.assemble(tmp_path, output, save={"format": "PNG", "compress_level": 1})

    with Image.open(output) as image:
        assert image.format == "PNG"


def test_arbitrary_output_format(tmp_path: Path) -> None:
    _tile(tmp_path, 0, 0)
    output = tmp_path / "map.data"

    maptiles.assemble(tmp_path, output, save={"format": "BMP"})

    with Image.open(output) as image:
        assert image.format == "BMP"


@pytest.mark.parametrize("conflict", (OnConflict.SKIP, OnConflict.RENAME))
def test_output_replaced(tmp_path: Path, conflict: OnConflict) -> None:
    _tile(tmp_path, 0, 0)
    output = tmp_path / "map.jpg"
    output.write_bytes(b"previous")

    result = maptiles.assemble(tmp_path, output, Options(on_conflict=conflict))

    assert result.output == output
    assert output.read_bytes() != b"previous"


def test_tile_size(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _tile(tmp_path, 0, 0)
    _tile(tmp_path, 1, 0)
    sizes = [maptiles.Size(2, 2), maptiles.Size(4, 4)]
    images = [Image.new("RGB", tuple(size)) for size in sizes]
    monkeypatch.setattr(maptiles, "_size", lambda *args: sizes.pop(0))
    monkeypatch.setattr(maptiles, "_decode", lambda *args: images.pop(0))

    output = tmp_path / "map.png"
    maptiles.assemble(tmp_path, output, save={"format": "PNG"})

    with Image.open(output) as image:
        assert image.size == (4, 2)


def test_tile_aspect_ratio(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = _tile(tmp_path, 0, 0)
    second = _tile(tmp_path, 1, 0)
    sizes = {
        first: maptiles.Size(2, 2),
        second: maptiles.Size(4, 2),
    }
    monkeypatch.setattr(maptiles, "_size", lambda path, options: sizes[path])

    with pytest.raises(exceptions.ConversionError, match="aspect ratio"):
        maptiles.assemble(tmp_path, tmp_path / "map.jpg")


def test_cancelled(tmp_path: Path) -> None:
    _tile(tmp_path, 0, 0)

    with pytest.raises(exceptions.MergeInterrupted):
        maptiles.assemble(tmp_path, tmp_path / "map.jpg", cancelled=lambda: True)
