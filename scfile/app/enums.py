from enum import StrEnum, auto


class CliCommand(StrEnum):
    """CLI commands."""

    CONVERT = auto()
    ANIMATE = auto()
    MAPCACHE = auto()
    MAPTILES = auto()


class AnimateCommand(StrEnum):
    """Animation subcommands."""

    ARMS = auto()
    BODY = auto()
    FACE = auto()


class OutputLayout(StrEnum):
    """Output directory layout."""

    ROOTED = auto()
    RELATIVE = auto()
    DUMP = auto()


class TaskKind(StrEnum):
    """Application operations."""

    CONVERT = auto()
    ANIMATE = auto()
    MAPCACHE = auto()
    MAPTILES = auto()


class TaskOutcome(StrEnum):
    """Final state of an application task."""

    EMPTY = auto()
    COMPLETED = auto()
    PARTIAL = auto()
    FAILED = auto()
    CANCELLED = auto()


class UpdateStatus(StrEnum):
    """Application update check status."""

    ERROR = auto()
    UPTODATE = auto()
    AVAILABLE = auto()
