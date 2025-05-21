from enum import StrEnum


class Prefix(StrEnum):
    """Colored labels for console output."""

    INFO = "[b blue]INFO:[/]"
    WARN = "[b yellow]WARN:[/]"
    ERROR = "[b red]ERROR:[/]"
    INVALID = "[b red]INVALID INPUT:[/]"
    EXCEPTION = "[b red]UNEXPECTED ERROR:[/]"
