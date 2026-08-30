import locale
from typing import Literal

from scfile import __documentation__ as DOCS


type Lang = Literal["EN", "RU"]
type DocsLang = Literal["en", "ru"]

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


def docs_language(lang: Lang) -> DocsLang:
    match lang:
        case "RU":
            return "ru"
        case _:
            return "en"


LANG: Lang = system_language()
DOCS_LANG: DocsLang = docs_language(LANG)
DOCS_URL: str = f"https://{DOCS}/{DOCS_LANG}"
