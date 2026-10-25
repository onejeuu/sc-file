import json
import re
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any

from .mdat.models import Note, State
from .reports import Diagnostic


JSON_COMMENTS = re.compile(r'("(?:\\.|[^"\\])*")|//[^\r\n]*|/\*[\s\S]*?\*/')


@dataclass(frozen=True)
class Source:
    path: Path
    size: int
    sha256: str


@dataclass(frozen=True)
class BlockDefinition:
    source: Path
    block_id: int
    metadata: int
    type: str
    icon: str
    color: tuple[float, float, float, float]


@dataclass(frozen=True)
class ObjectDefinition:
    source: Path
    object_id: str
    network_id_candidate: int
    generated: bool
    model: str | None
    material_lib: str | None
    aabb: str | None
    behaviour: str | None
    invisible_for_players: bool
    collision: str | None
    category: str | None


@dataclass
class Catalog:
    root: Path
    blocks: dict[int, BlockDefinition] = field(default_factory=dict)
    objects: tuple[ObjectDefinition, ...] = ()
    sources: list[Source] = field(default_factory=list)
    notes: list[Diagnostic] = field(default_factory=list)
    registry_complete: bool = True

    def block(self, state: State) -> BlockDefinition | None:
        return self.blocks.get(state.value)

    def object(self, network_id: int | None) -> ObjectDefinition | None:
        return (
            self.objects[network_id]
            if self.registry_complete and network_id is not None and 0 <= network_id < len(self.objects)
            else None
        )


def load(root: Path) -> Catalog:
    result = Catalog(root.resolve())
    assets = result.root / "configs" / "assets"

    def document(path: Path) -> Any:
        raw = path.read_bytes()
        result.sources.append(Source(path, len(raw), sha256(raw).hexdigest()))
        return json.loads(JSON_COMMENTS.sub(lambda match: match[1] or "", raw.decode("utf-8-sig")))

    blocks_path = assets / "pda" / "map_blocks.json"
    if blocks_path.exists():
        for row in document(blocks_path):
            value = BlockDefinition(
                blocks_path,
                row["id"],
                row["meta"],
                row["type"],
                row["iconName"],
                (row["red"], row["green"], row["blue"], row["alpha"]),
            )
            key = value.block_id | value.metadata << 12
            if key in result.blocks:
                result.notes.append(Diagnostic(blocks_path, None, Note("file", 0, f"Duplicate block state {key}")))
            result.blocks[key] = value
    else:
        result.notes.append(Diagnostic(blocks_path, None, Note("file", 0, "Block metadata file is unavailable")))

    definitions: dict[str, tuple[Path, dict[str, Any], bool]] = {}
    for namespace in sorted(assets.iterdir()):
        for path in sorted((namespace / "items").rglob("*.json")):
            try:
                data = document(path)
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                result.registry_complete = False
                result.notes.append(Diagnostic(path, None, Note("file", 0, str(error))))
                continue
            for row in data if isinstance(data, list) else (data,):
                if not isinstance(row, dict) or row.get("type") != "game_object":
                    continue
                name = row.get("object_id")
                if not isinstance(name, str):
                    result.registry_complete = False
                    result.notes.append(
                        Diagnostic(path, None, Note("file", 0, "Object definition has no string object_id"))
                    )
                    continue
                if name in definitions:
                    result.registry_complete = False
                    result.notes.append(Diagnostic(path, None, Note("file", 0, f"Duplicate object_id {name}")))
                definitions[name] = path, row, False

    mines = assets / "stalker" / "mine_presets.json"
    if mines.exists():
        for name in document(mines):
            key = "mine_" + name
            if key in definitions:
                result.registry_complete = False
                result.notes.append(Diagnostic(mines, None, Note("file", 0, f"Generated ID duplicates {key}")))
            definitions[key] = mines, {"behaviour": "mining_point"}, True
    else:
        result.registry_complete = False
        result.notes.append(Diagnostic(mines, None, Note("file", 0, "Generated mine definitions are unavailable")))

    def inherited(name: str, ancestors: tuple[str, ...] = ()) -> dict[str, Any]:
        path, row, _ = definitions[name]
        if name in ancestors:
            result.registry_complete = False
            result.notes.append(Diagnostic(path, None, Note("file", 0, f"Inheritance cycle at {name}")))
            return {}
        parent = row.get("extends_gameobject")
        values = inherited(parent, ancestors + (name,)) if isinstance(parent, str) and parent in definitions else {}
        if isinstance(parent, str) and parent not in definitions:
            result.registry_complete = False
            result.notes.append(Diagnostic(path, None, Note("file", 0, f"Parent definition {parent} is unavailable")))
        values.update(row)
        return {
            key: value for key, value in values.items() if not (isinstance(value, str) and value.lower() == "<default>")
        }

    rows = []
    for index, name in enumerate(sorted(definitions, key=lambda value: value.encode("utf-16-be"))):
        path, _, generated = definitions[name]
        values = inherited(name)
        rows.append(
            ObjectDefinition(
                path,
                name,
                index,
                generated,
                values.get("model"),
                values.get("material_lib"),
                values.get("aabb"),
                values.get("behaviour"),
                values.get("invisible_for_players", False),
                values.get("collision"),
                values.get("category"),
            )
        )
    result.objects = tuple(rows)
    return result
