from pathlib import Path

import pytest

from scfile.convert.base import convert, ensure_unique_path
from scfile.core.options import UserOptions
from scfile.exceptions import FileNotFound
from tests.conftest import FakeDecoder, FakeEncoder


def test_missing_file(temp: Path):
    with pytest.raises(FileNotFound):
        convert(FakeDecoder, FakeEncoder, temp / "missing.mcsb")


def test_default_dir(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    convert(FakeDecoder, FakeEncoder, src)
    assert (temp / "model.obj").read_bytes() == b"data"


def test_custom_dir(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "out"
    convert(FakeDecoder, FakeEncoder, src, out)
    assert (out / "model.obj").read_bytes() == b"data"


def test_custom_file(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "result.obj"
    convert(FakeDecoder, FakeEncoder, src, out)
    assert out.read_bytes() == b"data"


def test_custom_file_no_suffix(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "noext"
    convert(FakeDecoder, FakeEncoder, src, out)
    assert (out / "model.obj").read_bytes() == b"data"


def test_overwrite(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "model.obj"
    out.write_bytes(b"old")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="overwrite"))
    assert out.read_bytes() == b"data"


def test_skip(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "model.obj"
    out.write_bytes(b"old")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="skip"))
    assert out.read_bytes() == b"old"


def test_rename(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "model.obj"
    out.write_bytes(b"old")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="rename"))
    assert out.read_bytes() == b"old"
    assert (temp / "model (1).obj").read_bytes() == b"data"


def test_rename_multiple(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"x")
    (temp / "model.obj").write_bytes(b"1")
    (temp / "model (1).obj").write_bytes(b"2")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="rename"))
    assert (temp / "model (2).obj").read_bytes() == b"x"


def test_out_dir_created(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "nested" / "deep"
    convert(FakeDecoder, FakeEncoder, src, out)
    assert (out / "model.obj").read_bytes() == b"data"


def test_ensure_unique_first(temp: Path):
    assert ensure_unique_path(temp / "new.obj") == temp / "new.obj"


def test_ensure_unique_second(temp: Path):
    (temp / "file.obj").write_bytes(b"x")
    assert ensure_unique_path(temp / "file.obj") == temp / "file (1).obj"


def test_ensure_unique_third(temp: Path):
    (temp / "file.obj").write_bytes(b"x")
    (temp / "file (1).obj").write_bytes(b"x")
    assert ensure_unique_path(temp / "file.obj") == temp / "file (2).obj"
