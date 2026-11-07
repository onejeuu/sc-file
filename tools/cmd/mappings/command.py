import gzip
import hashlib
import json
import struct
import webbrowser
import zipfile
from collections.abc import Callable
from functools import partial
from pathlib import Path

import click
from rich import print
from rich.markup import escape

from scfile.formats.mca import mappings as block_mappings
from tools.cmd import tools
from tools.paths import ROOT

from . import config, extract


REPORTS = ROOT / "reports" / "mappings"
GROUPS = ROOT / "assets" / "mappings" / "groups.json.gz"
TEMPLATE = ROOT / "assets" / "mappings" / "viewer.html.gz"
STATE = REPORTS / ".state.json"
VERSIONS = {"stalcraft": 1, "minecraft": 1}


def save_state(state: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def read_state() -> dict:
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))

    except (OSError, ValueError):
        return {}

    return state if isinstance(state, dict) else {}


def file_hash(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, partial(hashlib.blake2b, digest_size=32)).hexdigest()


def signature(version: int, paths: tuple[Path, ...]) -> dict:
    return {
        "version": version,
        "files": {path.resolve().as_posix(): file_hash(path) for path in paths},
    }


def outputs_exist(directory: Path, texture_field: str) -> bool:
    index = directory / "index.json"
    report = directory / "report.json"
    if not index.is_file() or not report.is_file():
        return False

    try:
        records = json.loads(index.read_text(encoding="utf-8"))

    except (OSError, ValueError):
        return False

    if not isinstance(records, list):
        return False

    if texture_field == "primary":
        paths = (view.get("primary") for record in records for view in record.get("views", ()))
    else:
        paths = (record.get(texture_field) for record in records)

    paths = list(paths)
    return any(paths) and all(not path or (directory / path).is_file() for path in paths)


def ensure_asset(
    name: str,
    label: str,
    source: Path,
    catalog: Path,
    extract_source: Callable[[Path], None],
    texture_field: str,
    state: dict,
    force: bool,
) -> None:
    current = signature(VERSIONS[name], (source, catalog))
    directory = REPORTS / name
    if not force and state.get(name) == current and outputs_exist(directory, texture_field):
        print(f"{label} up to date.")
        return

    print(f"{label} extracting textures.")
    extract_source(source)
    state[name] = current
    save_state(state)


def clean_groups(source: object) -> dict:
    if not isinstance(source, dict) or not isinstance(source.get("groups"), list):
        raise ValueError("groups.json.gz must contain a groups array.")

    used_sync_ids = set()
    groups = []
    for number, group in enumerate(source["groups"], 1):
        if not isinstance(group, dict):
            raise ValueError(f"Group {number} must be an object.")

        ids = group.get("ids")
        if not isinstance(ids, list) or len(ids) < 2:
            raise ValueError(f"Group {number} must contain at least two IDs.")
        if any(type(value) is not int or not 0 <= value <= 4095 for value in ids):
            raise ValueError(f"Group {number} contains an invalid block ID.")
        if len(set(ids)) != len(ids):
            raise ValueError(f"Group {number} contains duplicate IDs.")

        sync = group.get("sync", [])
        if not isinstance(sync, list):
            raise ValueError(f"Group {number} sync must be an array.")

        clean_sync = []
        for sync_number, members in enumerate(sync, 1):
            if not isinstance(members, list) or len(members) < 2:
                raise ValueError(f"Group {number}, sync {sync_number} must contain at least two IDs.")
            if any(type(value) is not int or value not in ids for value in members):
                raise ValueError(f"Group {number}, sync {sync_number} contains an invalid member.")
            if len(set(members)) != len(members) or any(value in used_sync_ids for value in members):
                raise ValueError(f"Group {number}, sync {sync_number} contains duplicate members.")
            used_sync_ids.update(members)
            clean_sync.append(members)

        groups.append({"ids": ids, "sync": clean_sync})

    return {"groups": groups}


def build_viewer() -> Path:
    stalcraft = json.loads((REPORTS / "stalcraft/index.json").read_text(encoding="utf-8"))
    minecraft = json.loads((REPORTS / "minecraft/index.json").read_text(encoding="utf-8"))
    with gzip.open(GROUPS, "rt", encoding="utf-8") as file:
        groups = clean_groups(json.load(file))
    base = dict(block_mappings.BUILTIN[block_mappings.DEFAULT])

    with gzip.open(TEMPLATE, "rt", encoding="utf-8") as file:
        template = file.read()
    if template.count("/*__DATA__*/") != 1:
        raise ValueError("Invalid Mapping Editor template: expected one data placeholder.")

    payload = json.dumps(
        {
            "stalcraft": stalcraft,
            "minecraft": minecraft,
            "base": base,
            "assetsBase": "./",
            "groups": groups,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", r"<\/")
    viewer = REPORTS / "viewer.html"
    viewer.write_text(template.replace("/*__DATA__*/", "BOOT = " + payload + ";"), encoding="utf-8")
    print(f"Viewer: [cyan]{escape(str(viewer))}[/]")
    return viewer


@tools.command()
@click.option("--force", is_flag=True, help="Rebuild both resource indexes.")
@click.option("--run", "open_browser", is_flag=True, help="Open Mapping Editor after building.")
def mappings(force: bool, open_browser: bool) -> None:
    try:
        stalcraft_source, minecraft_source = config.read()
        state = read_state()

        ensure_asset(
            "stalcraft",
            "[bold cyan]Stalcraft[/]",
            stalcraft_source,
            extract.STALCRAFT_CATALOG,
            extract.extract_stalcraft,
            "primary",
            state,
            force,
        )

        ensure_asset(
            "minecraft",
            "[bold magenta]Minecraft[/]",
            minecraft_source,
            extract.MINECRAFT_CATALOG,
            extract.extract_minecraft,
            "texture",
            state,
            force,
        )

        viewer = build_viewer()

        if open_browser and not webbrowser.open(viewer.resolve().as_uri()):
            print(
                f"[red]Could not open browser:[/] "
                f"[cyan]{escape(str(viewer))}[/]"
            )

    except (OSError, ValueError, KeyError, struct.error, zipfile.BadZipFile) as error:
        raise click.ClickException(str(error)) from None
