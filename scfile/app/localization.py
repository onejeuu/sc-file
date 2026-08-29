import locale
from typing import Literal


type Lang = Literal["EN", "RU"]

_LOCALE_PREFIXES: dict[Lang, tuple[str, ...]] = {
    "RU": ("russian", "ru_"),
}


def system_language() -> Lang:
    try:
        language = (locale.getlocale()[0] or "").lower()

    except Exception:
        return "EN"

    for lang, prefixes in _LOCALE_PREFIXES.items():
        if language.startswith(prefixes):
            return lang

    return "EN"


LANG: Lang = system_language()
