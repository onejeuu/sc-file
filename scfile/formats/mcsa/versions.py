from typing import TypeAlias

from scfile.structures.flags import Flag


Version: TypeAlias = float

SUPPORTED_VERSIONS: list[Version] = [
    7.0,
    8.0,
    9.0,
    10.0,
    11.0,
    12.0,
]


VERSION_MAP: dict[Version, list[Flag]] = {
    7.0: [Flag.SKELETON, Flag.UV, Flag.NORMALS, Flag.COLORS],
    8.0: [Flag.SKELETON, Flag.UV, Flag.NORMALS, Flag.TANGENTS, Flag.COLORS],
    9.0: [Flag.SKELETON, Flag.UV, Flag.UV2, Flag.NORMALS, Flag.TANGENTS, Flag.COLORS],
}
