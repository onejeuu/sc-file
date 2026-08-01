"""CLI error and warning messages."""

from rich import print

from scfile import exceptions, types
from scfile.app.tasks import Failure, Item
from scfile.consts import INVALID_INPUT_HINT
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


def task_message(event: object) -> None:
    """Render one application task event."""

    if isinstance(event, Item):
        if event.detail:
            print(L.DONE, event.detail)
        elif event.written:
            print(L.DONE, f"'{event.source}'")
        else:
            print(L.INFO, f"Skipped '{event.source}'")
        return

    if not isinstance(event, Failure):
        return

    error = event.error
    location = error.location if isinstance(error, exceptions.ScFileException) else None
    message = f"'{location or event.source}': {error}"
    if isinstance(error, exceptions.BinaryStructureError):
        print(L.ERROR, message, INVALID_INPUT_HINT)
    elif isinstance(error, exceptions.ScFileException):
        print(L.ERROR, message)
    else:
        print(L.EXCEPTION, f"File '{event.source}' {error!r}.", INVALID_INPUT_HINT)

    if event.traceback:
        print(event.traceback)
