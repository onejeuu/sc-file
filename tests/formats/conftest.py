from pathlib import Path


ASSETS = Path(__file__).parents[1] / "assets" / "formats"


def export(
    decoder,
    encoder,
    source: Path,
    options=None,
) -> bytes:
    """Decode one fixture and encode its regression output."""

    with decoder(source, options) as dec:
        content = dec.decode()

    with encoder(content, options) as enc:
        return enc.to_bytes()


def assert_binary(actual: bytes, expected: bytes) -> None:
    """Compare binary data without rendering its full diff."""

    __tracebackhide__ = True

    if actual == expected:
        return

    shared = min(len(actual), len(expected))
    offset = next((index for index in range(shared) if actual[index] != expected[index]), shared)
    actual_byte = f"0x{actual[offset]:02X}" if offset < len(actual) else "EOF"
    expected_byte = f"0x{expected[offset]:02X}" if offset < len(expected) else "EOF"
    raise AssertionError(
        f"Binary data differs at offset {offset:,}: actual {actual_byte}, expected {expected_byte} "
        f"(length {len(actual):,} / {len(expected):,})."
    )
