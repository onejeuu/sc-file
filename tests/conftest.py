import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from scfile.core.context import UserOptions


@pytest.fixture
def assets(request: Any) -> Path:
    current_test_dir = Path(request.module.__file__).resolve().parent
    return current_test_dir / "assets"


@pytest.fixture
def options() -> UserOptions:
    return UserOptions(overwrite=True)


@pytest.fixture
def temp() -> Generator[Path, Any, None]:
    with tempfile.TemporaryDirectory(prefix="scfiletest_") as dir:
        yield Path(dir)
