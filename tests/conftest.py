import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def assets(request: Any) -> Path:
    current_test_dir = Path(request.module.__file__).resolve().parent
    return current_test_dir / "assets"


@pytest.fixture
def temp():
    with tempfile.TemporaryDirectory(prefix="scfiletest") as dir:
        yield Path(dir)
