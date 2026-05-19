from pathlib import Path

import pytest

from scfile.convert.base import convert, ensure_unique_path
from scfile.core.options import UserOptions
from scfile.exceptions import FileNotFound
from tests.conftest import FakeDecoder, FakeEncoder


def test_file_not_found(temp: Path):
    with pytest.raises(FileNotFound):
        convert(FakeDecoder, FakeEncoder, temp / "missing.mcsb")


def test_output_default(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    convert(FakeDecoder, FakeEncoder, src)
    assert (temp / "model.obj").exists()


def test_output_dir(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out_dir = temp / "out"
    convert(FakeDecoder, FakeEncoder, src, out_dir)
    assert (out_dir / "model.obj").exists()


def test_output_file(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "result.obj"
    convert(FakeDecoder, FakeEncoder, src, out)
    assert out.exists()


def test_skip_existing(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "model.obj"
    out.write_bytes(b"existing")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="skip"))
    assert out.read_bytes() == b"existing"


def test_rename(temp: Path):
    src = temp / "model.mcsb"
    src.write_bytes(b"data")
    out = temp / "model.obj"
    out.write_bytes(b"existing")
    convert(FakeDecoder, FakeEncoder, src, temp, UserOptions(on_conflict="rename"))
    assert out.exists()
    assert (temp / "model (1).obj").exists()


def test_ensure_unique_first(temp: Path):
    p = temp / "new.obj"
    result = ensure_unique_path(p)
    assert result == p


def test_ensure_unique_creates_counter(temp: Path):
    p = temp / "file.obj"
    p.write_bytes(b"x")
    result = ensure_unique_path(p)
    assert result == temp / "file (1).obj"


def test_ensure_unique_multiple(temp: Path):
    p = temp / "file.obj"
    (temp / "file.obj").write_bytes(b"x")
    (temp / "file (1).obj").write_bytes(b"x")
    result = ensure_unique_path(p)
    assert result == temp / "file (2).obj"
