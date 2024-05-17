from pathlib import Path

from scfile import OlDecoder


def test_to_dds_dxt5(assets: Path):
    with OlDecoder(assets / "dxt5" / "input.ol") as decoder:
        converted = decoder.to_dds().content

    with open(assets / "dxt5" / "output.dds", "rb") as fp:
        expected = fp.read()

    assert converted == expected
