import locale

import pytest

from scfile.app import localization


@pytest.mark.parametrize("name", ("Russian_Russia", "ru_RU"))
def test_russian(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(locale, "getlocale", lambda: (name, "UTF-8"))

    assert localization.system_language() == "RU"


@pytest.mark.parametrize("name", ("English_United States", None))
def test_fallback(name: str | None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(locale, "getlocale", lambda: (name, "UTF-8"))

    assert localization.system_language() == "EN"
