from scfile.options import DEFAULT_MODEL_FORMATS, DEFAULT_SKELETON_FORMATS, Options


def test_default_model_formats_standard():
    opts = Options(skeleton=False)
    assert opts.default_model_formats == DEFAULT_MODEL_FORMATS


def test_default_model_formats_on_skeleton():
    opts = Options(skeleton=True)
    assert opts.default_model_formats == DEFAULT_SKELETON_FORMATS
