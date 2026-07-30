from typing import TypeAlias

from scfile.structures.models import Feature, Features


Version: TypeAlias = float

SUPPORTED_VERSIONS: list[Version] = [
    7.0,
    8.0,
    9.0,
    10.0,
    11.0,
    12.0,
    15.0,
]
"""Supported MCSA format versions."""

VERSION_MAP: dict[Version, Features] = {
    7.0: (Feature.SKELETON, Feature.UV, Feature.NORMALS, Feature.COLORS),
    8.0: (Feature.SKELETON, Feature.UV, Feature.NORMALS, Feature.TANGENTS, Feature.COLORS),
    9.0: (
        Feature.SKELETON,
        Feature.UV,
        Feature.UV2,
        Feature.NORMALS,
        Feature.TANGENTS,
        Feature.COLORS,
    ),
}
"""Mapping of MCSA versions to feature flags (version floor semantics)."""
