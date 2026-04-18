from scfile import __version__


class FBX:
    VERSION = 7400
    HEADER_VERSION = 1003
    HEADER = b"Kaydara FBX Binary  \x00\x1a\x00"
    FILE_ID = b"\x28\xb5\x2f\xfd\x8e\xb5\x4e\x54\x9f\x38\x1e\xb9\xe6\x2b\x92\xad"
    NULL_NODE = b"\x00" * 13
    CREATOR = b"onejeuu/sc-file v" + __version__.encode()


class DEFAULT:
    pass
