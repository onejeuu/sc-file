from scfile.convert.regions import Bounds, Offset, Region, Size


def test_key() -> None:
    assert Region.parse("-2.3") == Region(-2, 3)
    assert Region.parse("r.-2.3") is None
    assert Region.parse("0.0.0") is None


def test_bounds() -> None:
    bounds = Bounds.parse((Region(-2, 3), Region(1, -1)))

    assert bounds == Bounds(left=-2, top=-1, right=1, bottom=3)
    assert bounds.size(Size(width=128, height=64)) == Size(width=512, height=320)
    assert bounds.offset(Region(1, 3), Size(width=128, height=64)) == Offset(left=384, top=256)
