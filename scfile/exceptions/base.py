class ScFileException(Exception):
    """Base exception for scfile library."""

    pass


class DecodingError(ScFileException):
    """Base exception occurring while file decoding."""

    pass


class EncodingError(ScFileException):
    """Base exception occurring while file encoding."""

    pass


class ParsingError(ScFileException):
    """Base exception occurring due to unexpected file structure."""

    pass


class UnsupportedError(ScFileException):
    """Base exception occurring intentionally for unsupported formats."""

    pass
