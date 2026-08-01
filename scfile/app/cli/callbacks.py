"""Click callbacks for global command options."""

import click

from scfile import __version__ as SEMVER
from scfile.app.cli import messages
from scfile.consts import SUPPORTED_NBT, SUPPORTED_SUFFIXES
from scfile.enums import UpdateStatus
from scfile.utils import updates
from scfile.utils.versions import Version


def version_callback(
    ctx: click.Context,
    param: click.Parameter | None,
    value: bool,
) -> None:
    """Print version information and exit."""

    if not value:
        return

    version = Version.parse(SEMVER)

    messages.echo(f"scfile, version {str(version)} {version.emoji if version else ''}")
    messages.echo(f"Supported Formats: {sorted(SUPPORTED_SUFFIXES)}")
    messages.echo(f"Supported NBTs: {sorted(SUPPORTED_NBT)}")

    ctx.exit()


def updates_callback(
    ctx: click.Context,
    param: click.Parameter | None,
    value: bool,
) -> None:
    """Check for updates and exit."""

    if not value:
        return

    check = updates.check(SEMVER)

    match check.status:
        case UpdateStatus.UPTODATE:
            messages.echo("✅ You are using the latest version", style="green")

        case UpdateStatus.AVAILABLE:
            messages.echo(f"🔄 Update available: {check.url}", style="blue")

        case UpdateStatus.ERROR:
            messages.error(f"❌ Could not check for updates: {check.message}")
            if check.url:
                messages.hint(f"Check manually: {check.url}")

    ctx.exit()
