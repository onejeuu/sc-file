"""Terminal output."""

from collections.abc import Iterable

from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text

from scfile.app.consts import ACCENT_COLOR, APPLICATION


CONSOLE = Console()


def print(
    renderable: RenderableType,
) -> None:
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
    _message("INFO", text, "blue")


def hint(text: str) -> None:
    _message("HINT", text, "cyan")


def warn(text: str) -> None:
    _message("WARN", text, "yellow")


def error(text: str) -> None:
    _message("ERROR", text, "red")


def unexpected(text: str) -> None:
    _message("UNEXPECTED ERROR", text, "red")


def invalid(text: str) -> None:
    _message("INVALID INPUT", text, "red")


def aborted(text: str) -> None:
    _message("ABORTED", text, "yellow")


def version(
    value: str,
    emoji: str,
    formats: Iterable[str],
    nbt: Iterable[str],
) -> None:
    title = Text(APPLICATION, style=ACCENT_COLOR)
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
