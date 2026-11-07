import tomllib
from pathlib import Path

import click

from tools.paths import ROOT


CONFIG = ROOT / "configs" / "mappings" / "config.toml"


def read(
    stalcraft_texarr: Path | None = None,
    minecraft_jar: Path | None = None,
) -> tuple[Path, Path]:
    try:
        with CONFIG.open("rb") as file:
            values = tomllib.load(file).get("paths", {})

    except FileNotFoundError:
        if stalcraft_texarr is None or minecraft_jar is None:
            raise click.UsageError(f"Copy 'config.example.toml' to '{CONFIG}'.") from None
        values = {}

    except tomllib.TOMLDecodeError as error:
        raise click.ClickException(f"Invalid configuration '{CONFIG}': {error}") from None

    if not isinstance(values, dict):
        raise click.ClickException(f"'[paths]' must be a table in '{CONFIG}'.")

    paths = []
    overrides = (stalcraft_texarr, minecraft_jar)
    for key, override in zip(("stalcraft_texarr", "minecraft_jar"), overrides):
        value = override if override is not None else values.get(key)
        if not isinstance(value, (str, Path)) or not str(value).strip():
            raise click.UsageError(f"Set '[paths].{key}' in '{CONFIG}'.")

        path = Path(value).expanduser()
        paths.append((ROOT.parent / path).resolve() if not path.is_absolute() else path.resolve())

    for label, path in (("Stalcraft", paths[0]), ("Minecraft", paths[1])):
        if not path.is_file():
            raise click.ClickException(f"{label} source file not found: '{path}'.")

    return paths[0], paths[1]
