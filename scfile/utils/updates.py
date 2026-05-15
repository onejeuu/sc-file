import json
import urllib.request
from typing import Any

from scfile import __repository__ as REPO
from scfile.enums import UpdateStatus as Status

from . import files, versions


TIMEOUT = 5


def fetch(url: str) -> dict[str, Any] | None:
    headers = {"User-Agent": f"{REPO}", "Cache-Control": "no-cache"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode())

    except Exception:
        return None


def current() -> str | None:
    try:
        commit = files.resource("commit")
        if commit.exists():
            return commit.read_text().strip()

    except Exception:
        pass

    return None


def _check_dev(v: versions.Version) -> tuple[Status, str]:
    sha = current()
    if not sha:
        url = f"https://github.com/{REPO}/releases/tag/{v.tag}"
        return (Status.ERROR, f"local commit sha not found. check manually: {url}")

    data = fetch(f"https://api.github.com/repos/{REPO}/commits/{v.tag}")
    if not data:
        return (Status.ERROR, "network error")

    remote_sha = data.get("sha")
    if remote_sha != sha:
        return (Status.AVAILABLE, f"https://github.com/{REPO}/releases/tag/{v.tag}")

    return (Status.UPTODATE, "")


def _check_release(v: versions.Version) -> tuple[Status, str]:
    latest = fetch(f"https://api.github.com/repos/{REPO}/releases/latest")
    if latest is None:
        return (Status.ERROR, "network error")

    tag = latest.get("tag_name", "")
    remote_v = versions.parse(tag)
    if remote_v and remote_v > v:
        return (Status.AVAILABLE, f"https://github.com/{REPO}/releases/tag/{tag}")

    return (Status.UPTODATE, "")


def check(semver: str) -> tuple[Status, str]:
    v = versions.parse(semver)
    if not v:
        return (Status.ERROR, f"invalid version format '{semver}'")

    if "dev" in str(v.suffix):
        return _check_dev(v)

    return _check_release(v)
