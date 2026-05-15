from typing import Any, TypeAlias

from scfile import __repository__ as REPO
from scfile import __version__ as SEMVER


Props: TypeAlias = list[tuple[Any, ...]]


class FBX:
    VERSION = 7400
    HEADER_VERSION = 1003
    HEADER = b"Kaydara FBX Binary  \x00\x1a\x00"
    FILE_ID = b"\x28\xb5\x2f\xfd\x8e\xb5\x4e\x54\x9f\x38\x1e\xb9\xe6\x2b\x92\xad"
    NULL_NODE = b"\x00" * 13
    CREATOR = f"{REPO} v{SEMVER}".encode()


class DEFAULT:
    SETTINGS: Props = [
        (b"UpAxis", b"int", b"Integer", b"", 1),
        (b"UpAxisSign", b"int", b"Integer", b"", 1),
        (b"FrontAxis", b"int", b"Integer", b"", 2),
        (b"FrontAxisSign", b"int", b"Integer", b"", 1),
        (b"CoordAxis", b"int", b"Integer", b"", 0),
        (b"CoordAxisSign", b"int", b"Integer", b"", 1),
        (b"UnitScaleFactor", b"double", b"Number", b"", 100.0),
        (b"TimeMode", b"enum", b"", b"", 11),
        (b"TimeSpanStart", b"KTime", b"Time", b"", 0),
        (b"TimeSpanStop", b"KTime", b"Time", b"", 0),
    ]

    MESH: Props = [
        (b"Lcl Translation", b"Lcl Translation", b"", b"A", 0.0, 0.0, 0.0),
        (b"Lcl Rotation", b"Lcl Rotation", b"", b"A", 0.0, 0.0, 0.0),
        (b"DefaultAttributeIndex", b"int", b"Integer", b"", 0),
        (b"InheritType", b"enum", b"", b"", 1),
    ]

    MATERIAL: Props = [
        (b"DiffuseColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
        (b"EmissiveColor", b"Color", b"", b"A", 1.0, 1.0, 1.0),
        (b"EmissiveFactor", b"Number", b"", b"A", 0.0),
        (b"AmbientColor", b"Color", b"", b"A", 0.05, 0.05, 0.05),
        (b"AmbientFactor", b"Number", b"", b"A", 0.0),
        (b"BumpFactor", b"double", b"Number", b"", 0.0),
        (b"SpecularColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
        (b"SpecularFactor", b"Number", b"", b"A", 0.0),
        (b"Shininess", b"Number", b"", b"A", 0.0),
        (b"ShininessExponent", b"Number", b"", b"A", 0.0),
        (b"ReflectionColor", b"Color", b"", b"A", 0.8, 0.8, 0.8),
        (b"ReflectionFactor", b"Number", b"", b"A", 0.0),
    ]

    CURVE: Props = [
        (b"d|X", b"Number", b"", b"A", 0.0),
        (b"d|Y", b"Number", b"", b"A", 0.0),
        (b"d|Z", b"Number", b"", b"A", 0.0),
    ]
