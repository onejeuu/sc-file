"""Application updates checking."""

import json
import urllib.request
from typing import Any, NamedTuple

from scfile import __repository__ as REPO
from scfile.enums import UpdateStatus as Status

from . import files
from .versions import Version


TIMEOUT = 5


class UpdateCheck(NamedTuple):
    status: Status
    message: str
    url: str


def _fetch(url: str) -> dict[str, Any] | None:
    headers = {"User-Agent": f"{REPO}", "Cache-Control": "no-cache"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode())

    except Exception:
        return None


def current() -> str | None:
    """Read local commit SHA from bundled file."""

    try:
        commit = files.resource("commit")
        if commit.exists():
            return commit.read_text().strip()

    except Exception:
        pass

    return None


def _check_dev(v: Version) -> UpdateCheck:
    sha = current()
    if not sha:
        url = f"https://github.com/{REPO}/releases/tag/{v.tag}"
        return UpdateCheck(Status.ERROR, "local commit sha not found", url)

    data = _fetch(f"https://api.github.com/repos/{REPO}/commits/{v.tag}")
    if not data:
        return UpdateCheck(Status.ERROR, "network error", "")

    remote_sha = data.get("sha")
    if remote_sha != sha:
        return UpdateCheck(Status.AVAILABLE, "", f"https://github.com/{REPO}/releases/tag/{v.tag}")

    return UpdateCheck(Status.UPTODATE, "", "")


def _check_release(v: Version) -> UpdateCheck:
    data = _fetch(f"https://api.github.com/repos/{REPO}/releases/latest")
    if data is None:
        return UpdateCheck(Status.ERROR, "network error", "")

    tag = data.get("tag_name", "")
    remote_v = Version.parse(tag)
    if not remote_v:
        return UpdateCheck(Status.ERROR, f"invalid remote version format '{tag}'", "")

    if remote_v and remote_v > v:
        return UpdateCheck(Status.AVAILABLE, "", f"https://github.com/{REPO}/releases/tag/{tag}")

    return UpdateCheck(Status.UPTODATE, "", "")


def check(semver: str) -> UpdateCheck:
    """Check GitHub for a newer version."""

    v = Version.parse(semver)
    if not v:
        return UpdateCheck(Status.ERROR, f"invalid version format '{semver}'", "")

    if v.is_dev:
        return _check_dev(v)

    return _check_release(v)
