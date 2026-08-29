from pathlib import Path

from scfile.app.gui.threads import RequestTokens
from scfile.app.gui.workers.mapcache import Scanner


def test_scanner_checks_selected_outputs(tmp_path: Path) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    (source / "reg.1.-2.mdat").write_bytes(b"data")
    output = tmp_path / "region"
    output.mkdir()
    (output / "r.1.-2.mca").touch()

    requests = RequestTokens()
    request = requests.next()
    scanner = Scanner(requests)
    results = []
    scanner.scanned.connect(lambda *result: results.append(result))

    scanner.scan(request, str(source), str(output))

    assert results == [(request, 1, True, None)]


def test_scanner_ignores_other_outputs(tmp_path: Path) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    (source / "reg.1.-2.mdat").write_bytes(b"data")
    output = tmp_path / "region"
    output.mkdir()
    (output / "r.0.0.mca").touch()

    requests = RequestTokens()
    request = requests.next()
    scanner = Scanner(requests)
    results = []
    scanner.scanned.connect(lambda *result: results.append(result))

    scanner.scan(request, str(source), str(output))

    assert results == [(request, 1, False, None)]
