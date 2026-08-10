"""Terminal output."""

from collections.abc import Iterable

from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text


CONSOLE = Console()


def print(
    renderable: RenderableType,
) -> None:
    """Render terminal content."""

    CONSOLE.print(renderable, highlight=False)


def _message(
    label: str,
    text: str,
    style: str,
) -> None:
    message = Text()
    message.append(f"{label}: ", style=f"bold {style}")
    message.append(text)
    CONSOLE.print(message, highlight=False)


def info(text: str) -> None:
    """Show informational text."""

    _message("INFO", text, "blue")


def hint(text: str) -> None:
    """Show additional guidance."""

    _message("HINT", text, "cyan")


def warn(text: str) -> None:
    """Show a warning."""

    _message("WARN", text, "yellow")


def error(text: str) -> None:
    """Show an error."""

    _message("ERROR", text, "red")


def unexpected(text: str) -> None:
    """Show an unexpected error."""

    _message("UNEXPECTED ERROR", text, "red")


def invalid(text: str) -> None:
    """Show invalid command input."""

    _message("INVALID INPUT", text, "red")


def aborted(text: str) -> None:
    """Show an aborted operation."""

    _message("ABORTED", text, "yellow")


def version(
    value: str,
    emoji: str,
    formats: Iterable[str],
    nbt: Iterable[str],
) -> None:
    """Show version and supported inputs."""

    title = Text("scfile", style="bold yellow")
    title.append(f" {value}")
    if emoji:
        title.append(f" {emoji}")

    support = Table.grid(padding=(0, 2))
    support.add_column(style="bold")
    support.add_column(style="cyan")
    support.add_row("Formats", "  ".join(sorted(formats)))
    support.add_row("NBT", "  ".join(sorted(nbt)))

    CONSOLE.print(title)
    CONSOLE.print()
    CONSOLE.print(support)
