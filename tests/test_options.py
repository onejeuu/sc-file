from scfile.options import DEFAULT_MODEL_FORMATS, DEFAULT_SKELETON_FORMATS, Options


def test_animation_enables_skeleton() -> None:
    assert Options(model={"animation": True}).model.skeleton_enabled


def test_default_formats() -> None:
    assert Options().default_formats is DEFAULT_MODEL_FORMATS
    assert Options(model={"skeleton": True}).default_formats is DEFAULT_SKELETON_FORMATS
    assert Options(model={"animation": True}).default_formats is DEFAULT_SKELETON_FORMATS
