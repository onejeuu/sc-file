from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def assets(request: Any):
    current_test_dir = Path(request.module.__file__).resolve().parent
    return current_test_dir / "assets"
