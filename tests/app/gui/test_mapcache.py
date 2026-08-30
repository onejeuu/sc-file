from pathlib import Path

import pytest

from scfile.app.gui.threads import RequestTokens
from scfile.app.gui.workers.mapcache import Scanner


@pytest.mark.parametrize(
    ("target", "overlap"),
    (("r.1.-2.mca", True), ("r.0.0.mca", False)),
)
def test_overlap(tmp_path: Path, target: str, overlap: bool) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    (source / "reg.1.-2.mdat").write_bytes(b"data")
    output = tmp_path / "region"
    output.mkdir()
    (output / target).touch()

    requests = RequestTokens()
    request = requests.next()
    scanner = Scanner(requests)
    results = []
    scanner.scanned.connect(lambda *result: results.append(result))

    scanner.scan(request, str(source), str(output))

    assert results == [(request, 1, overlap, None)]
