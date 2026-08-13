from collections.abc import Callable

import pytest
from rich.text import Text

from scfile.app.cli import console


@pytest.mark.parametrize(
    "render",
    [
        console.info,
        console.hint,
        console.warn,
        console.error,
        console.unexpected,
        console.invalid,
        console.aborted,
    ],
)
def test_messages_render_text(render: Callable[[str], None], monkeypatch: pytest.MonkeyPatch) -> None:
    values: list[object] = []
    monkeypatch.setattr(console.CONSOLE, "print", lambda value, **kwargs: values.append(value))

    render("message")

    assert len(values) == 1
    assert isinstance(values[0], Text)


def test_print_forwards_renderable(monkeypatch: pytest.MonkeyPatch) -> None:
    values: list[object] = []
    renderable = Text("value")
    monkeypatch.setattr(console.CONSOLE, "print", lambda value, **kwargs: values.append(value))

    console.print(renderable)

    assert values == [renderable]


@pytest.mark.parametrize("emoji", ["", "🍉"])
def test_version_renders_support_table(emoji: str, monkeypatch: pytest.MonkeyPatch) -> None:
    values: list[object] = []
    monkeypatch.setattr(console.CONSOLE, "print", lambda value=None, **kwargs: values.append(value))

    console.version("6.0.0", emoji, [".mcsb", ".mic"], ["prefs", "sd1"])

    assert len(values) == 3
    assert isinstance(values[0], Text)
