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
