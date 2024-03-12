from pathlib import Path

from scfile.file.mic.decoder import MicDecoder


def test_to_png(assets: Path):
    with MicDecoder(assets / "input.mic") as decoder:
        converted = decoder.to_png().result

    with open(assets / "output.png", "rb") as fp:
        expected = fp.read()

    assert converted == expected
