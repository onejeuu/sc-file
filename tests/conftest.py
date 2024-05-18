import os
import tempfile
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def assets(request: Any):
    current_test_dir = Path(request.module.__file__).resolve().parent
    return current_test_dir / "assets"


@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        yield file.name
    os.remove(file.name)
