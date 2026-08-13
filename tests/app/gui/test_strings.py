from scfile.app.gui.strings import DATA


def test_languages_have_same_entries() -> None:
    assert DATA["EN"].keys() == DATA["RU"].keys()
