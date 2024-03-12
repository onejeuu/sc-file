from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def assets(request: Any):
    test_dir = Path(request.module.__file__).resolve().parent
    assets_dir = test_dir / "assets"
    return assets_dir
