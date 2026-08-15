import json
from functools import cache
from typing import Any

from tools.paths import ROOT

from .runner import PlanError


MAPPINGS = ROOT / "assets" / "audit"
VERSION = 1


@cache
def read(name: str) -> dict[str, Any]:
    path = MAPPINGS / f"animate.{name}.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))

    except FileNotFoundError:
        raise PlanError(f"Animation mappings do not exist: {path}") from None

    except (OSError, json.JSONDecodeError) as error:
        raise PlanError(f"Cannot read animation mappings '{path}': {error}") from None

    if value.get("version") != VERSION:
        raise PlanError(f"Unsupported animation mappings version in '{path}'.")
    return value


def animations(name: str) -> dict[str, list[str]]:
    value = read(name).get("animations")
    if not isinstance(value, dict):
        raise PlanError(f"Animation mappings have no 'animations' object: {MAPPINGS / f'animate.{name}.json'}")
    return value
