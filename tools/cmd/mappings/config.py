import tomllib
from pathlib import Path

import click

from tools.paths import ROOT


CONFIG = ROOT / "configs" / "mappings" / "config.toml"


def read() -> tuple[Path, Path]:
    try:
        with CONFIG.open("rb") as file:
            values = tomllib.load(file).get("paths", {})

    except FileNotFoundError:
        raise click.UsageError(f"Copy 'config.example.toml' to '{CONFIG}'.") from None

    except tomllib.TOMLDecodeError as error:
        raise click.ClickException(f"Invalid configuration '{CONFIG}': {error}") from None

    if not isinstance(values, dict):
        raise click.ClickException(f"'[paths]' must be a table in '{CONFIG}'.")

    paths = []
    for key in ("stalcraft_texarr", "minecraft_jar"):
        value = values.get(key)
        if not isinstance(value, str) or not value.strip():
            raise click.UsageError(f"Set '[paths].{key}' in '{CONFIG}'.")

        path = Path(value).expanduser()
        paths.append((ROOT.parent / path).resolve() if not path.is_absolute() else path.resolve())

    for label, path in zip(("STALCRAFT TEXARR", "Minecraft 1.12.2 JAR"), paths):
        if not path.is_file():
            raise click.ClickException(f"{label} not found: '{path}'.")

    return paths[0], paths[1]
