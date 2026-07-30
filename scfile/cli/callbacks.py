"""Click callbacks for global command options."""

from typing import Optional

import click
from rich import print

from scfile import __version__ as SEMVER
from scfile.consts import SUPPORTED_NBT, SUPPORTED_SUFFIXES
from scfile.enums import UpdateStatus
from scfile.utils import updates
from scfile.utils.versions import Version


def version_callback(
    ctx: click.Context,
    param: Optional[click.Parameter],
    value: bool,
) -> None:
    """Print version information and exit."""

    if not value:
        return

    version = Version.parse(SEMVER)

    print(f"scfile, version {str(version)} {version.emoji if version else ''}")
    print(f"Supported Formats: {sorted(SUPPORTED_SUFFIXES)}")
    print(f"Supported NBTs: {sorted(SUPPORTED_NBT)}")

    ctx.exit()


def updates_callback(
    ctx: click.Context,
    param: Optional[click.Parameter],
    value: bool,
) -> None:
    """Check for updates and exit."""

    if not value:
        return

    check = updates.check(SEMVER)

    match check.status:
        case UpdateStatus.UPTODATE:
            print("[green]✅ You are using the latest version[/]")

        case UpdateStatus.AVAILABLE:
            print(f"[blue]🔄 Update available:[/] {check.url}")

        case UpdateStatus.ERROR:
            url = f"\n[yellow]Check manually:[/] {check.url}" if check.url else ""
            print(f"[red]❌ Could not check for updates:[/] {check.message} {url}".strip())

    ctx.exit()
