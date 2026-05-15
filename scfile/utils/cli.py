import click
from rich import print

from scfile import __version__ as SEMVER
from scfile import types
from scfile.consts import CLI
from scfile.enums import L, UpdateStatus

from . import updates, versions


def check_feature_unsupported(
    user_formats: types.Formats,
    unsupported_formats: types.Formats,
    feature: str,
) -> None:
    """Checks that user formats contain unsupported feature."""
    matching_formats = list(filter(lambda fmt: fmt in unsupported_formats, user_formats))

    if bool(matching_formats):
        suffixes = ", ".join(map(lambda fmt: fmt.suffix, matching_formats))
        print(L.WARN, f"Specified formats [b]({suffixes})[/] doesn't support {feature}.")


def version_callback(ctx: click.Context, param: click.Parameter, value: bool):
    if value:
        version = versions.parse(SEMVER)

        print(f"scfile, version {str(version)} {version.emoji if version else ''}")
        print(CLI.FORMATS)
        print(CLI.NBT)

    ctx.exit()


def updates_callback(ctx: click.Context, param: click.Parameter, value: bool):
    if value:
        status, info = updates.check(SEMVER)

        match status:
            case UpdateStatus.UPTODATE:
                print("[green]✅ You are using the latest version[/]")

            case UpdateStatus.AVAILABLE:
                print(f"[blue]🔄 Update available: {info}[/]")

            case UpdateStatus.ERROR:
                print(f"[red]❌ Could not check for updates:[/] {info}")

    ctx.exit()
