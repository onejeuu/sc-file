from pathlib import Path

from scfile.utils.files import destination, resolve, walk


def test_resolve(tmp_path: Path) -> None:
    parent = tmp_path / "assets"
    child = parent / "models"
    child.mkdir(parents=True)
    source = child / "model.mcsb"
    source.write_bytes(b"")

    assert resolve([source, parent, source]) == [parent.resolve()]
    assert resolve([tmp_path / "missing"]) == []


def test_walk(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    (models / "model.mcsb").write_bytes(b"")
    (models / "image.mic").write_bytes(b"")
    (models / "notes.txt").write_bytes(b"")

    entries = list(walk([tmp_path], whitelist=[".mcsb", ".mic"]))

    assert {Path(entry.path).name for entry in entries} == {"model.mcsb", "image.mic"}
    assert {Path(entry.relpath) for entry in entries} == {Path("models/model.mcsb"), Path("models/image.mic")}


def test_parent_path(tmp_path: Path) -> None:
    source = tmp_path / "model.mcsb"
    source.write_bytes(b"")

    (entry,) = walk([source], whitelist=[".mcsb"], parent=True)

    assert entry.relpath == "model.mcsb"


def test_destination() -> None:
    target = destination("models/model.obj", relative=True, output="output")

    assert target is not None
    assert Path(target) == Path("output/models")
    assert destination("models/model.obj", relative=False, output="output") == "output"
    assert destination("models/model.obj", relative=True, output=None) is None
