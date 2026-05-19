import os
import sys
from pathlib import Path
from unittest.mock import patch

from scfile.utils.files import destination, resolve, resource, walk


def test_destination():
    assert destination("a/b.txt", True, "out") == os.path.join("out", "a")
    assert destination("a/b.txt", False, "out") == "out"
    assert destination("a/b.txt", True, None) is None
    assert destination("a/b.txt", False, None) is None


def test_resolve(temp: Path):
    a = temp / "a.mcsa"
    b = temp / "b.mcsa"
    a.write_text("")
    b.write_text("")

    assert resolve([a]) == [a.resolve()]
    assert resolve([temp / "missing.mcsa"]) == []
    assert len(list(resolve([a, a]))) == 1
    assert len(list(resolve([a, b]))) == 2

    parent = temp / "root"
    child = parent / "sub"
    child.mkdir(parents=True)
    (child / "x.mcsa").write_text("")
    assert resolve([parent, child / "x.mcsa"]) == [parent.resolve()]
    assert resolve([child / "x.mcsa", parent]) == [parent.resolve()]


def test_walk_files(temp: Path):
    (temp / "a.mcsa").write_text("")
    (temp / "b.mcsb").write_text("")
    (temp / "c.txt").write_text("")
    result = list(walk([temp], whitelist=[".mcsa", ".mcsb"]))
    names = {os.path.basename(e.path) for e in result}
    assert names == {"a.mcsa", "b.mcsb"}


def test_walk_dirs(temp: Path):
    sub = temp / "sub"
    sub.mkdir()
    (sub / "d.mcsa").write_text("")
    (sub / "e.mcsb").write_text("")
    result = list(walk([temp]))
    names = {os.path.basename(e.path) for e in result}
    assert names == {"d.mcsa", "e.mcsb"}


def test_walk_parent_relpath(temp: Path):
    sub = temp / "sub"
    sub.mkdir()
    (sub / "d.mcsa").write_text("")
    result = list(walk([sub / "d.mcsa"], parent=True))
    assert result[0].relpath == "d.mcsa"


def test_walk_empty_dir(temp: Path):
    (temp / "empty").mkdir()
    assert list(walk([temp / "empty"])) == []


def test_walk_no_match(temp: Path):
    (temp / "a.txt").write_text("")
    assert list(walk([temp], whitelist=[".mcsa"])) == []


def test_walk_deep_nesting(temp: Path):
    deep = temp / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "f.mcsa").write_text("")
    result = list(walk([temp]))
    assert len(result) == 1
    assert os.path.basename(result[0].path) == "f.mcsa"


def test_resource_meipass():
    setattr(sys, "_MEIPASS", "/fake/meipass")

    try:
        assert resource("file.txt") == Path("/fake/meipass/file.txt")

    finally:
        delattr(sys, "_MEIPASS")


def test_resource_dev():
    p = resource("file.txt")
    assert p.name == "file.txt"


def test_walk_permission_error(temp: Path):
    locked = temp / "locked"
    locked.mkdir()
    (locked / "a.mcsa").write_text("")
    (temp / "b.mcsa").write_text("")

    scandir = os.scandir

    def _scandir(path):
        if os.path.samefile(path, str(locked)):
            raise PermissionError
        return scandir(path)

    with patch("os.scandir", side_effect=_scandir):
        result = list(walk([temp]))
        names = {os.path.basename(e.path) for e in result}
        assert "b.mcsa" in names
        assert "a.mcsa" not in names
