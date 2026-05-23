from scfile.consts import DefaultModelFormats
from scfile.core.options import Options


def test_default_model_formats_standard():
    opts = Options(skeleton=False)
    assert opts.default_model_formats == DefaultModelFormats.STANDARD


def test_default_model_formats_on_skeleton():
    opts = Options(skeleton=True)
    assert opts.default_model_formats == DefaultModelFormats.ON_SKELETON
