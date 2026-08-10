from pathlib import Path

from scfile.app.files import count, destination, resolve, walk


def test_resolve(tmp_path: Path) -> None:
    parent = tmp_path / "assets"
    child = parent / "models"
    child.mkdir(parents=True)
    source = child / "model.mcsb"
    source.write_bytes(b"")

    assert resolve([source, parent, source]) == [parent.resolve()]
    assert resolve([tmp_path / "missing"]) == []


def test_resolve_many_files(tmp_path: Path) -> None:
    files = [tmp_path / f"{index}.mic" for index in range(64)]
    for path in files:
        path.write_bytes(b"")

    assert resolve(reversed(files)) == sorted(files)


def test_walk(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    (models / "model.mcsb").write_bytes(b"")
    (models / "image.mic").write_bytes(b"")
    (models / "notes.txt").write_bytes(b"")

    entries = list(walk([tmp_path], filters=[".mcsb", ".mic"]))

    assert {Path(entry.path).name for entry in entries} == {"model.mcsb", "image.mic"}
    assert {Path(entry.root) for entry in entries} == {tmp_path}


def test_file_root(tmp_path: Path) -> None:
    source = tmp_path / "model.mcsb"
    source.write_bytes(b"")

    (entry,) = walk([source], filters=[".mcsb"])

    assert entry.root == str(source)


def test_count(tmp_path: Path) -> None:
    (tmp_path / "first.mic").write_bytes(b"")
    (tmp_path / "second.ol").write_bytes(b"")
    (tmp_path / "ignored.txt").write_bytes(b"")

    assert count([tmp_path], filters=[".mic", ".ol"]) == 2


def test_destination() -> None:
    target = destination("assets/models/model.obj", "assets", "output")

    assert target is not None
    assert Path(target) == Path("output/models")
    assert destination("assets/models/model.obj", None, "output") == "output"
    assert destination("assets/models/model.obj", "assets", None) is None
