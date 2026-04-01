import click
from rich import print

from scfile import __version__
from scfile.consts import CLI


def version_to_emoji(version: str) -> str:
    base, *pre = version.split("-")
    major, minor, patch = map(int, base.split("."))
    prehash = sum(map(ord, pre[0])) if pre else 0
    index = (major * 1000 + minor * 100 + patch + prehash) % len(EMOJIS)
    return EMOJIS[index]


def callback(ctx: click.Context, param: click.Parameter, value: bool):
    if not value:
        return

    print(f"scfile, version {__version__} {version_to_emoji(__version__)}")
    print(CLI.FORMATS)
    print(CLI.NBT)

    ctx.exit()


EMOJIS = [
    "🍓",
    "🍒",
    "🍑",
    "🍋",
    "🍉",
    "🍍",
    "🍇",
    "🍏",
    "🥝",
    "🥥",
    "🌽",
    "🌭",
    "🍕",
    "🍔",
    "🧀",
    "🥨",
    "🍤",
    "🍫",
    "🍦",
    "🍩",
    "🍪",
    "🍭",
    "🍰",
    "☕️",
    "🧃",
]
