from scfile import types
from scfile.enums import L


def check_feature_unsupported(
    user_formats: types.Formats,
    unsupported_formats: types.Formats,
    feature: str,
) -> None:
    """Checks that user formats contain unsupported feature."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: fmt.suffix, matching_formats))
        print(L.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature}.")
