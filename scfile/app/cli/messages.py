"""CLI error and warning messages."""

from rich import print

from scfile import exceptions, types
from scfile.enums import FileFormat, L
from scfile.options import HandlerOptions
from scfile.registry import REGISTRY
from scfile.structures.models import Feature, Features


def error_message(
    error: exceptions.ScFileException,
) -> str:
    """Format a library error for command-line output."""

    if error.location:
        return f"'{error.location}': {error}"

    return str(error)


def warn_unsupported_features(
    formats: types.Formats,
    options: HandlerOptions,
) -> None:
    """Warn when explicitly selected formats omit requested model data."""

    requested: Features = ()
    if options.skeleton_enabled:
        requested += (Feature.SKELETON,)

    if options.animation:
        requested += (Feature.ANIMATION,)

    unsupported: dict[FileFormat, Features] = {}
    for fmt in formats:
        features = tuple(feature for feature in requested if not REGISTRY.formats[fmt].supports(feature))
        if features:
            unsupported[fmt] = features

    if not unsupported:
        return

    details = "; ".join(f"{fmt.upper()} ({', '.join(features)})" for fmt, features in unsupported.items())
    print(L.WARN, f"Requested model feature is not supported by: {details}.")
