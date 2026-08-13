import json
from pathlib import Path

import pytest

from scfile.app import updates
from scfile.app.enums import UpdateStatus
from scfile.app.version import Version


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("v6.1.2", Version(6, 1, 2)),
        ("6.1.2-dev", Version(6, 1, 2, "dev")),
        ("broken", None),
    ],
)
def test_version_parse(value: str, expected: Version | None) -> None:
    assert Version.parse(value) == expected


def test_version() -> None:
    dev = Version(6, 0, 0, "dev")
    release = Version(6, 0, 0)

    assert dev.is_dev
    assert dev.tag == "v6.0-dev"
    assert release.tag == "v6.0.0"
    assert dev < release
    assert dev != object()
    assert release.emoji


def test_current(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    commit = tmp_path / "commit"
    commit.write_text("abc123\n")
    monkeypatch.setattr(updates.files, "resource", lambda _: commit)

    assert updates.current() == "abc123"


def test_current_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates.files, "resource", lambda _: (_ for _ in ()).throw(OSError()))

    assert updates.current() is None


@pytest.mark.parametrize(
    ("semver", "payload", "status"),
    [
        ("6.0.0", {"tag_name": "v6.1.0"}, UpdateStatus.AVAILABLE),
        ("6.0.0", {"tag_name": "v6.0.0"}, UpdateStatus.UPTODATE),
        ("6.0.0", {"tag_name": "broken"}, UpdateStatus.ERROR),
        ("broken", {}, UpdateStatus.ERROR),
    ],
)
def test_release(
    semver: str,
    payload: dict[str, str],
    status: UpdateStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(updates, "_fetch", lambda _: payload)

    assert updates.check(semver).status is status


def test_release_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_fetch", lambda _: None)

    assert updates.check("6.0.0").status is UpdateStatus.ERROR


@pytest.mark.parametrize(
    ("local", "remote", "status"),
    [
        (None, None, UpdateStatus.ERROR),
        ("abc", None, UpdateStatus.ERROR),
        ("abc", {"sha": "def"}, UpdateStatus.AVAILABLE),
        ("abc", {"sha": "abc"}, UpdateStatus.UPTODATE),
    ],
)
def test_dev(
    local: str | None,
    remote: dict[str, str] | None,
    status: UpdateStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(updates, "current", lambda: local)
    monkeypatch.setattr(updates, "_fetch", lambda _: remote)

    assert updates.check("6.0.0-dev").status is status


def test_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self) -> bytes:
            return json.dumps({"sha": "abc"}).encode()

    monkeypatch.setattr(updates.urllib.request, "urlopen", lambda *args, **kwargs: Response())
    assert updates._fetch("https://example.invalid") == {"sha": "abc"}


def test_fetch_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates.urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(OSError()))
    assert updates._fetch("https://example.invalid") is None
