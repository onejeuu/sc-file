from collections.abc import Iterator

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> Iterator[CliRunner]:
    # CliRunner owns its isolated filesystem; tests must not use the process cwd.
    yield CliRunner()
