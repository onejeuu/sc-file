import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from scfile.enums import UpdateStatus as Status
from scfile.utils import updates


def _fake_urlopen(body: Any, status: int = 200):
    class _Response:
        def read(self):
            return json.dumps(body).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    return lambda req, timeout: _Response()


def test_fetch_ok():
    with patch("urllib.request.urlopen", _fake_urlopen({"key": "val"})):
        assert updates._fetch("http://x") == {"key": "val"}


def test_fetch_error():
    with patch("urllib.request.urlopen", side_effect=Exception):
        assert updates._fetch("http://x") is None


def test_check_invalid():
    assert updates.check("abc") == (Status.ERROR, "invalid version format 'abc'", "")


def test_check_dev_no_sha():
    with patch.object(updates, "current", return_value=None):
        check = updates.check("1.0.0-dev")
        assert check.status == Status.ERROR


def test_check_dev_network_error():
    with patch.object(updates, "current", return_value="abc123"):
        with patch.object(updates, "_fetch", return_value=None):
            check = updates.check("1.0.0-dev")
            assert check.status == Status.ERROR


def test_check_dev_uptodate():
    with patch.object(updates, "current", return_value="abc123"):
        with patch.object(updates, "_fetch", return_value={"sha": "abc123"}):
            check = updates.check("1.0.0-dev")
            assert check.status == Status.UPTODATE


def test_check_dev_available():
    with patch.object(updates, "current", return_value="abc123"):
        with patch.object(updates, "_fetch", return_value={"sha": "def456"}):
            check = updates.check("1.0.0-dev")
            assert check.status == Status.AVAILABLE


def test_check_release_network_error():
    with patch.object(updates, "_fetch", return_value=None):
        check = updates.check("1.0.0")
        assert check.status == Status.ERROR


def test_check_release_invalid_remote():
    with patch.object(updates, "_fetch", return_value={"tag_name": "bad"}):
        check = updates.check("1.0.0")
        assert check.status == Status.ERROR


def test_check_release_uptodate():
    with patch.object(updates, "_fetch", return_value={"tag_name": "v1.0.0"}):
        check = updates.check("1.0.0")
        assert check.status == Status.UPTODATE


def test_check_release_available():
    with patch.object(updates, "_fetch", return_value={"tag_name": "v2.0.0"}):
        check = updates.check("1.0.0")
        assert check.status == Status.AVAILABLE


def test_current_exists(temp: Path):
    commit = temp / "commit"
    commit.write_text("abc123\n")
    with patch.object(updates.files, "resource", return_value=commit):
        assert updates.current() == "abc123"


def test_current_missing(temp: Path):
    commit = temp / "commit"
    with patch.object(updates.files, "resource", return_value=commit):
        assert updates.current() is None


def test_current_error():
    with patch.object(updates.files, "resource", side_effect=Exception):
        assert updates.current() is None
