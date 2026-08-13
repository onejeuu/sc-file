from scfile.app.gui.strings import DATA


def test_languages() -> None:
    assert DATA["EN"].keys() == DATA["RU"].keys()
