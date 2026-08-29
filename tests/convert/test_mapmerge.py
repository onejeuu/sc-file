from pathlib import Path
from shutil import copyfile

import pytest
from PIL import Image

from scfile import exceptions
from scfile.convert import mapmerge
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

    assert mapmerge.scan(tmp_path) == {mapmerge.Region(-1, 2): expected}


def test_merge(tmp_path: Path) -> None:
    _tile(tmp_path, -1, 1)
    _tile(tmp_path, 0, 1)
    output = tmp_path / "output/map.jpg"

    result = mapmerge.merge(tmp_path, output)

    assert result == mapmerge.MergeResult(output, 2)
    with Image.open(output) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert image.size == (1344, 504)


def test_empty(tmp_path: Path) -> None:
    with pytest.raises(exceptions.ConversionError, match="No map tiles found"):
        mapmerge.merge(tmp_path, tmp_path / "map.jpg")


def test_output_format(tmp_path: Path) -> None:
    with pytest.raises(exceptions.ConversionError, match=r"\.jpg"):
        mapmerge.merge(tmp_path, tmp_path / "map.png")


@pytest.mark.parametrize("conflict", (OnConflict.SKIP, OnConflict.RENAME))
def test_output_replaced(tmp_path: Path, conflict: OnConflict) -> None:
    _tile(tmp_path, 0, 0)
    output = tmp_path / "map.jpg"
    output.write_bytes(b"previous")

    result = mapmerge.merge(tmp_path, output, Options(on_conflict=conflict))

    assert result.output == output
    assert output.read_bytes() != b"previous"


def test_tile_size(tmp_path: Path, monkeypatch) -> None:
    _tile(tmp_path, 0, 0)
    _tile(tmp_path, 1, 0)
    images = [Image.new("RGB", (2, 2)), Image.new("RGB", (3, 2))]
    monkeypatch.setattr(mapmerge, "_decode", lambda *args: images.pop(0))

    with pytest.raises(exceptions.ConversionError, match="tile size"):
        mapmerge.merge(tmp_path, tmp_path / "map.jpg")


def test_cancelled(tmp_path: Path) -> None:
    _tile(tmp_path, 0, 0)

    with pytest.raises(exceptions.MergeInterrupted):
        mapmerge.merge(tmp_path, tmp_path / "map.jpg", cancelled=lambda: True)
