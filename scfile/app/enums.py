from enum import StrEnum, auto


class CliCommand(StrEnum):
    """CLI commands."""

    ANIMATE = auto()
    CONVERT = auto()
    MAPCACHE = auto()


class AnimateCommand(StrEnum):
    """Animation subcommands."""

    ARMS = auto()
    BODY = auto()
    FACE = auto()


class OutputLayout(StrEnum):
    """Output directory layout."""

    FLAT = auto()
    RELATIVE = auto()
    ROOTED = auto()


class TaskKind(StrEnum):
    """Application operations."""

    CONVERT = auto()
    MAPCACHE = auto()
    ANIMATE = auto()


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
