from unittest.mock import MagicMock, patch

from scfile.enums import FileFormat, UpdateStatus
from scfile.utils.cli import (
    check_feature_unsupported,
    updates_callback,
    version_callback,
)
from scfile.utils.updates import UpdateCheck


def test_check_features():
    check_feature_unsupported(
        [FileFormat.OBJ],
        [FileFormat.FBX],
        "animations",
    )

    check_feature_unsupported(
        [FileFormat.OBJ, FileFormat.FBX],
        [FileFormat.FBX],
        "animations",
    )


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
    with patch("scfile.utils.cli.updates.check", return_value=UpdateCheck(UpdateStatus.UPTODATE, "", "")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()


def test_updates_error():
    ctx = MagicMock()
    with patch("scfile.utils.cli.updates.check", return_value=UpdateCheck(UpdateStatus.ERROR, "fail", "")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()


def test_updates_available():
    ctx = MagicMock()
    with patch("scfile.utils.cli.updates.check", return_value=UpdateCheck(UpdateStatus.AVAILABLE, "", "http://x")):
        updates_callback(ctx, None, True)
        ctx.exit.assert_called_once()
