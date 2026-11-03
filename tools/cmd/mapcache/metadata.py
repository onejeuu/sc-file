import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path

from tools.paths import ROOT

from .mdat.terrain import State


ASSETS = ROOT / "assets" / "mapcache"


@dataclass(frozen=True)
class BlockDefinition:
    source: Path
    block_id: int
    metadata: int
    type: str
    icon: str
    color: tuple[float, float, float, float]
    name: str | None = None


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
    hash64: int = 0


@dataclass
class Catalog:
    root: Path
    blocks: dict[int, BlockDefinition] = field(default_factory=dict)
    objects: tuple[ObjectDefinition, ...] = ()
    by_hash: dict[int, ObjectDefinition] = field(default_factory=dict)
    by_id: dict[str, ObjectDefinition] = field(default_factory=dict)
    biomes: dict[int, dict] = field(default_factory=dict)
    voxels: dict[str, dict] = field(default_factory=dict)
    registry_complete: bool = True
    notes: list = field(default_factory=list)

    def block(self, state: State) -> BlockDefinition | None:
        return self.blocks.get(state.value) or self.blocks.get(state.block_id)

    def object(self, object_id: int | None) -> ObjectDefinition | None:
        if object_id is None:
            return None
        return self.by_hash.get(object_id) or (self.objects[object_id] if 0 <= object_id < len(self.objects) else None)


def load() -> Catalog:
    result = Catalog(ASSETS)
    blocks_path = ASSETS / "blocks.json"
    with gzip.open(ASSETS / "mapcache.json.gz", "rt", encoding="utf-8") as stream:
        data = json.load(stream)
    result.biomes = {row["id"]: row for row in data["biomes"]}
    result.voxels = data["voxels"]
    names = json.loads(blocks_path.read_text(encoding="utf-8"))
    for row in data["states"]:
        value = int(row["state"], 16)
        result.blocks[value] = BlockDefinition(
            ASSETS / "mapcache.json.gz",
            row["block"],
            row["meta"],
            row["type"] or "",
            row["icon"] or "",
            tuple(row["color"]),
            names.get(str(row["block"])),
        )
    for state, name in names.items():
        value = int(state)
        result.blocks.setdefault(
            value,
            BlockDefinition(blocks_path, value & 0xFFF, value >> 12, "", "", (0, 0, 0, 0), name),
        )
    rows = []
    for row in data["objects"]:
        value = ObjectDefinition(
            ASSETS / "mapcache.json.gz",
            row["id"],
            row["index"],
            False,
            row["model"],
            row["material"],
            row["aabb"],
            row["behaviour"],
            row["invisible"],
            row["collision"],
            row["category"],
            int(row["hash"], 16),
        )
        rows.append(value)
        result.by_hash[value.hash64] = value
        result.by_id[value.object_id] = value
    result.objects = tuple(sorted(rows, key=lambda row: row.network_id_candidate))
    return result
