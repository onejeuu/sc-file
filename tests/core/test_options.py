from scfile.consts import DefaultModelFormats
from scfile.core.options import UserOptions


def test_default_model_formats_standard():
    opts = UserOptions(parse_skeleton=False)
    assert opts.default_model_formats == DefaultModelFormats.STANDARD


def test_default_model_formats_on_skeleton():
    opts = UserOptions(parse_skeleton=True)
    assert opts.default_model_formats == DefaultModelFormats.ON_SKELETON
