from typing import NamedTuple, Optional

import click
from rich import print

from scfile import __version__
from scfile.consts import CLI


class Version(NamedTuple):
    major: int
    minor: int
    patch: int
    suffix: Optional[str] = None

    @property
    def emoji(self) -> str:
        suffixhash = sum(map(ord, self.suffix)) if self.suffix else 0
        index = (self.major * 1000 + self.minor * 100 + self.patch + suffixhash) % len(EMOJIS)
        return EMOJIS[index]

    @property
    def tag(self) -> str:
        if self.suffix == "dev":
            return f"v{self.major}.{self.minor}-dev"
        return f"v{self}"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}{f'-{self.suffix}' if self.suffix else ''}"


def parse(semver: str) -> Version | None:
    try:
        base, _, suffix = semver.removeprefix("v").partition("-")
        major, minor, patch = map(int, base.split("."))
        return Version(major, minor, patch, suffix or None)

    except (ValueError, TypeError):
        return None


def callback(ctx: click.Context, param: click.Parameter, value: bool):
    if value:
        version = parse(__version__)

        print(f"scfile, version {str(version)} {version.emoji if version else ''}")
        print(CLI.FORMATS)
        print(CLI.NBT)

        ctx.exit()


EMOJIS = [
    "🌭",
    "🌽",
    "🍇",
    "🍉",
    "🍋",
    "🍌",
    "🍍",
    "🍏",
    "🍑",
    "🍒",
    "🍓",
    "🍔",
    "🍕",
    "🍤",
    "🍦",
    "🍩",
    "🍪",
    "🍫",
    "🍭",
    "🍰",
    "🥝",
    "🥥",
    "🥨",
    "🧀",
]
