from pathlib import Path

from scfile.convert import decoders
from tools.audit.schemas import Animation, Bone, Image, Mesh, Model, Texture


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "configs" / "audit.toml"
REPORTS = ROOT / "reports" / "audit"

DECODERS = decoders()
FORMATS = tuple(sorted(DECODERS))

# Broken files in game assets
EXCLUDE = (
    "customitems/models/blocks/skafa.mcmtl.mcsb",
    "vegetation/models/wrk/optical.mic",
    "customitems/models/blocks/things/prestige_teleport.mcvd",
    "gloomycore/colliders/krovosos_clone/collider.mcvd",
    "gloomycore/colliders/pseudodog_clone/collider.mcvd",
    "gloomycore/colliders/tushkan_clone/collider.mcvd",
)

TABLES = {
    Model: "models.csv",
    Mesh: "meshes.csv",
    Bone: "bones.csv",
    Animation: "animations.csv",
    Texture: "textures.csv",
    Image: "images.csv",
}
FORMATS_CSV = "formats.csv"
ERRORS_JSONL = "errors.jsonl"
FILES = (*TABLES.values(), FORMATS_CSV, ERRORS_JSONL)
