from enum import StrEnum


class Prefix(StrEnum):
    INFO = "[b blue]INFO:[/]"
    WARN = "[b yellow]WARN:[/]"
    ERROR = "[b red]ERROR:[/]"
    CLIERROR = "[b red]CLI ERROR:[/]"
    EXCEPTION = "[b red]UNEXPECTED ERROR:[/]"
