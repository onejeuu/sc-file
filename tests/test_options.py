from scfile.options import DEFAULT_MODEL_FORMATS, DEFAULT_SKELETON_FORMATS, ConvertOptions, HandlerOptions


def test_animation_enables_skeleton() -> None:
    assert HandlerOptions(animation=True).skeleton_enabled


def test_default_formats() -> None:
    assert ConvertOptions().default_formats is DEFAULT_MODEL_FORMATS
    assert ConvertOptions(handlers=HandlerOptions(skeleton=True)).default_formats is DEFAULT_SKELETON_FORMATS
    assert ConvertOptions(handlers=HandlerOptions(animation=True)).default_formats is DEFAULT_SKELETON_FORMATS
