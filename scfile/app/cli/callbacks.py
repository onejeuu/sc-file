import click

from scfile import __version__ as SEMVER
from scfile.app import updates
from scfile.app.cli import console
from scfile.app.enums import UpdateStatus
from scfile.app.version import Version
from scfile.enums import FileFormat
from scfile.formats import registry


def version_callback(
    ctx: click.Context,
    param: click.Parameter | None,
    value: bool,
) -> None:
    """Print version information and exit."""

    if not value:
        return

    version = Version.parse(SEMVER)
    console.version(
        str(version),
        version.emoji if version else "",
        (format.suffix for format in registry.decoders),
        registry.aliases[FileFormat.NBT],
    )

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
            console.info("✅ You are using the latest version")

        case UpdateStatus.AVAILABLE:
            console.info(f"🔄 Update available: {check.url}")

        case UpdateStatus.ERROR:
            console.error(f"❌ Could not check for updates: {check.message}")
            if check.url:
                console.hint(f"Check manually: {check.url}")

    ctx.exit()
