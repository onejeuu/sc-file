from typing import TypeAlias


Version: TypeAlias = float
FlagsCount: TypeAlias = int

VERSION_FLAGS: dict[Version, FlagsCount] = {
    7.0: 4,
    8.0: 5,
    10.0: 6,
    11.0: 6,
}

SUPPORTED_VERSIONS: list[Version] = list(VERSION_FLAGS.keys())
