import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp() -> Generator[Path, None, None]:
    path = Path(tempfile.mkdtemp(prefix="scfiletest"))
    yield path
    shutil.rmtree(path)
