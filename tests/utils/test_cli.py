from unittest.mock import MagicMock, patch

from scfile.enums import UpdateStatus
from scfile.cli.callbacks import (
    updates_callback,
    version_callback,
)
from scfile.utils.updates import UpdateCheck


def test_version_noop():
    ctx = MagicMock()
    version_callback(ctx, None, False)
    ctx.exit.assert_not_called()


def test_version():
    ctx = MagicMock()
    version_callback(ctx, None, True)
    ctx.exit.assert_called_once()


def test_updates_noop():
    ctx = MagicMock()
    updates_callback(ctx, None, False)
    ctx.exit.assert_not_called()


def test_updates_ok():
    ctx = MagicMock()
    with patch("scfile.cli.callbacks.updates.check", return_value=UpdateCheck(UpdateStatus.UPTODATE, "", "")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()


def test_updates_error():
    ctx = MagicMock()
    with patch("scfile.cli.callbacks.updates.check", return_value=UpdateCheck(UpdateStatus.ERROR, "fail", "")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()


def test_updates_available():
    ctx = MagicMock()
    with patch("scfile.cli.callbacks.updates.check", return_value=UpdateCheck(UpdateStatus.AVAILABLE, "", "http://x")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()
