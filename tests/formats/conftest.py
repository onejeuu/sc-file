from pathlib import Path
from tests.fixtures import ASSETS as ROOT_ASSETS


ASSETS = ROOT_ASSETS / "formats"


def export(
    decoder,
    encoder,
    source: Path,
    options=None,
) -> bytes:
    with decoder(source, options) as dec:
        content = dec.decode()

    with encoder(content, options) as enc:
        return enc.to_bytes()
