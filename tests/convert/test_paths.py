from pathlib import Path

import pytest

from scfile import exceptions
from scfile.convert import paths
from scfile.options import Options


def test_source(tmp_path: Path) -> None:
    file = tmp_path / "source.bin"
    directory = tmp_path / "directory"
    file.write_bytes(b"")
    directory.mkdir()

    assert paths.source(file) == file

    for path in (directory, tmp_path / "missing.bin"):
        with pytest.raises(exceptions.FileNotFound):
            paths.source(path)


def test_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    directory = tmp_path / "output"
    file = directory / "renamed.png"

    assert paths.destination(source, directory, ".png") == directory / "source.png"
    assert paths.destination(source, file, ".png") == file


def test_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    output.write_bytes(b"existing")

    assert paths.output(source, output, ".png", Options()) == output
    assert paths.output(source, output, ".png", Options(on_conflict="skip")) is None
    assert paths.output(source, output, ".png", Options(on_conflict="rename")) == tmp_path / "output (1).png"


def test_unique(tmp_path: Path) -> None:
    path = tmp_path / "output.png"
    path.write_bytes(b"")
    (tmp_path / "output (1).png").write_bytes(b"")

    assert paths.unique(path) == tmp_path / "output (2).png"
