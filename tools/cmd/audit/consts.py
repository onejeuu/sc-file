# Known broken assets files
EXCLUDED: set[str] = {
    "_localized/ru/stalkerguide/handbook/articles/arthunt/artefakty_attachment_6.mic",  # raw jpeg
    "customitems/models/blocks/skafa.mcmtl.mcsb",  # fake mcmtl
    "stalker/textures/particlesFlat.map",  # unsupported format
    "vegetation/models/wrk/optical.mic",  # invalid structure
    "customitems/models/blocks/things/prestige_teleport.mcvd",  # invalid structure
    "gloomycore/colliders/krovosos_clone/collider.mcvd",  # invalid structure
    "gloomycore/colliders/pseudodog_clone/collider.mcvd",  # invalid structure
    "gloomycore/colliders/tushkan_clone/collider.mcvd",  # invalid structure
}
