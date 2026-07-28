from scfile.registry import REGISTRY
from tools.cmd.audit.schemas import Animation, Bone, Image, Mesh, Model, Texture
from tools.paths import ROOT


CONFIG = ROOT / "configs" / "audit.toml"
REPORTS = ROOT / "reports" / "audit"

DECODERS = {str(fmt): decoder for fmt, decoder in REGISTRY.decoders().items()}
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
