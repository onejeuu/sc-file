from scfile.utils.versions import Version


def test_string():
    assert str(Version(1, 2, 3)) == "1.2.3"
    assert str(Version(1, 2, 3, "dev")) == "1.2.3-dev"
    assert str(Version(0, 0, 1)) == "0.0.1"
    assert Version(1, 2, 3).tag == "v1.2.3"
    assert Version(1, 2, 3, "dev").tag == "v1.2-dev"
    assert Version(1, 2, 3, "beta").tag == "v1.2.3-beta"


def test_comparisons():
    assert Version(1, 0, 0) == Version(1, 0, 0)
    assert Version(1, 0, 0) != Version(2, 0, 0)
    assert Version(1, 0, 0) != Version(1, 0, 0, "rc1")
    assert Version(1, 0, 0) < Version(2, 0, 0)
    assert Version(1, 0, 0) < Version(1, 0, 0, "rc1")
    assert Version(2, 0, 0) > Version(1, 0, 0)
    assert Version(1, 0, 0, "rc1") > Version(1, 0, 0)
    assert Version(1, 0, 0) != "1.0.0"
    assert Version(1, 0, 0) != 73


def test_sort():
    v = [
        Version(2, 0, 0),
        Version(1, 5, 0),
        Version(1, 5, 0, "beta"),
        Version(1, 0, 0),
        Version(1, 0, 0, "rc1"),
    ]
    assert sorted(v) == [
        Version(1, 0, 0),
        Version(1, 0, 0, "rc1"),
        Version(1, 5, 0),
        Version(1, 5, 0, "beta"),
        Version(2, 0, 0),
    ]


def test_emoji():
    assert Version(1, 0, 0).emoji
    assert Version(99, 99, 99, "foo").emoji


def test_parse():
    assert Version.parse("1.2.3") == Version(1, 2, 3)
    assert Version.parse("v1.2.3") == Version(1, 2, 3)
    assert Version.parse("1.2.3-dev") == Version(1, 2, 3, "dev")
    assert Version.parse("0.0.0") == Version(0, 0, 0)
    assert Version.parse(" 1.2.3 ") == Version(1, 2, 3)
    assert Version.parse("abc") is None
    assert Version.parse("") is None
    assert Version.parse("1.2") is None
    assert Version.parse("v1.2.3.4") is None
