from pathlib import Path

import pytest

from scfile import exceptions
from scfile.convert.mapcache import group, merge, scan
from scfile.options import Options


def test_group() -> None:
    paths = [
        Path("r.0.0.mdat"),
        Path("reg.1.-1.mdat"),
        Path("invalid.mdat"),
    ]

    assert group(paths) == {
        (0, 0): [Path("r.0.0.mdat")],
        (1, -1): [Path("reg.1.-1.mdat")],
    }


def test_scan(tmp_path: Path) -> None:
    (tmp_path / "r.0.0.mdat").write_bytes(b"data")
    (tmp_path / "empty.mdat").write_bytes(b"")
    (tmp_path / "cached.bck.mdat").write_bytes(b"data")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "r.1.0.mdat").write_bytes(b"data")

    result = scan(tmp_path)

    assert {path.name for path in result.paths} == {"r.0.0.mdat", "r.1.0.mdat"}
    assert not result.errors


def test_scan_cancel(tmp_path: Path) -> None:
    (tmp_path / "r.0.0.mdat").write_bytes(b"data")

    result = scan(tmp_path, lambda: True)

    assert not result.paths
    assert not result.errors


def test_merge_cancel(tmp_path: Path) -> None:
    with pytest.raises(exceptions.MergeInterrupted):
        merge((0, 0), [tmp_path / "r.0.0.mdat"], tmp_path, Options(), lambda: True)


def test_merge_backup(tmp_path: Path) -> None:
    source = Path(__file__).parents[1] / "assets/formats/region/source/r.0.0.mdat"
    target = tmp_path / "r.0.0.mca"
    target.write_bytes(b"previous")

    result = merge((0, 0), [source, source], tmp_path, Options())

    assert result.filename == target.name
    assert result.chunks > 0
    assert target.exists()
    assert target.with_suffix(".mca.bck").read_bytes() == b"previous"
