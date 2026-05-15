from dataclasses import dataclass
from typing import Optional


@dataclass
class Version:
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

    def _key(self):
        return self.major, self.minor, self.patch, self.suffix is not None, self.suffix or ""

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() < other._key()

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() == other._key()


def parse(semver: str) -> Version | None:
    try:
        base, _, suffix = semver.removeprefix("v").partition("-")
        major, minor, patch = map(int, base.split("."))
        return Version(major, minor, patch, suffix or None)

    except (ValueError, TypeError):
        return None


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
