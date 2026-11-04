import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory


_directory = TemporaryDirectory(prefix="sc-file-assets-")
ASSETS = Path(_directory.name)
with tarfile.open(Path(__file__).parent / "assets" / "assest.tar.gz", "r:gz") as archive:
    archive.extractall(ASSETS, filter="data")

ASSETS /= "assets"
