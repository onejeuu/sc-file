import click
from rich import print

from scfile import __version__
from scfile.consts import CLI


def version_to_emoji(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    index = (major * 1000 + minor * 100 + patch) % len(EMOJIS)
    return EMOJIS[index]


def callback(ctx: click.Context, param: click.Parameter, value: bool):
    if not value:
        return

    print(f"scfile, version {__version__} {version_to_emoji(__version__)}")
    print(CLI.FORMATS)
    print(CLI.NBT)

    ctx.exit()


EMOJIS = [
    "🍓", "🍒", "🍑", "🍋", "🍉",
    "🍍", "🍇", "🍏", "🥝", "🥥",
    "🌽", "🌭", "🍕", "🍔", "🧀",
    "🥨", "🍤", "🍫", "🍦", "🍩",
    "🍪", "🍭", "🍰", "☕️", "🧃"
]
