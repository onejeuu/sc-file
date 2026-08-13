from pathlib import Path

from scfile.app import files
from scfile.app.events import TaskError
from scfile.app.files import count, destination, resolve, scan, walk


def test_resolve(tmp_path: Path) -> None:
    parent = tmp_path / "assets"
    child = parent / "models"
    child.mkdir(parents=True)
    source = child / "model.mcsb"
    source.write_bytes(b"")

    assert resolve([source, parent, source]) == [parent.resolve()]
    assert resolve([tmp_path / "missing"]) == [tmp_path / "missing"]


def test_resolve_files(tmp_path: Path) -> None:
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


def test_scan_missing(tmp_path: Path) -> None:
    (issue,) = scan([tmp_path / "missing"])

    assert isinstance(issue, TaskError)
    assert isinstance(issue.error, FileNotFoundError)


def test_scan_access(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "denied"

    def denied(path: str):
        raise PermissionError(13, "Access is denied", path)

    monkeypatch.setattr("scfile.app.files.os.scandir", denied)
    (issue,) = scan([source])

    assert isinstance(issue, TaskError)
    assert issue.source == str(source)
    assert isinstance(issue.error, PermissionError)


def test_root(tmp_path: Path) -> None:
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


def test_resource(monkeypatch) -> None:
    monkeypatch.setattr(files.sys, "_MEIPASS", "bundle", raising=False)

    assert files.resource("asset") == Path("bundle/asset")


def test_scan_error(tmp_path: Path, monkeypatch) -> None:
    class Entry:
        path = str(tmp_path / "denied.mic")
        name = "denied.mic"

        def is_symlink(self) -> bool:
            raise PermissionError(13, "denied", self.path)

    class Entries:
        def __enter__(self):
            return [Entry()]

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(files.os, "scandir", lambda _: Entries())
    (issue,) = scan([tmp_path], filters=[".mic"])

    assert isinstance(issue, TaskError)
    assert isinstance(issue.error, PermissionError)


def test_scan_links(tmp_path: Path, monkeypatch) -> None:
    class Entry:
        path = str(tmp_path / "entry")
        name = "entry"

        def __init__(self, link: bool, directory: bool, file: bool) -> None:
            self.link, self.directory, self.file = link, directory, file

        def is_symlink(self) -> bool:
            return self.link

        def is_junction(self) -> bool:
            return False

        def is_dir(self) -> bool:
            return self.directory

        def is_file(self) -> bool:
            return self.file

    class Entries:
        def __enter__(self):
            return [Entry(True, False, False), Entry(False, False, False)]

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(files.os, "scandir", lambda _: Entries())
    assert not list(scan([tmp_path], filters=[".mic"]))
