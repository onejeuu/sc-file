import linecache
import traceback
from pathlib import Path

import click
from rich.console import Console

from scfile.enums import FileFormat
from scfile.options import Options
from scfile.formats import registry
from tools.cmd import tools

from . import tables


FORMATS = tuple(str(fmt) for fmt in registry.decoders)


def parser(exception: Exception) -> tuple[str, str, str] | None:
    found = None
    fallback = None

    for frame, lineno in traceback.walk_tb(exception.__traceback__):
        module = frame.f_globals.get("__name__", "")
        if not module.startswith("scfile."):
            continue

        item = (
            frame.f_code.co_name,
            linecache.getline(frame.f_code.co_filename, lineno).strip(),
            f"{module}:{lineno}",
        )
        fallback = item

        if item[0] == "parse" or item[0].startswith("_parse"):
            found = item

    return found or fallback


@tools.command()
@click.argument(
    "SOURCE",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "-F",
    "--format",
    type=click.Choice(FORMATS, case_sensitive=False),
    help="Source format.",
)
def info(source: Path, format: str | None) -> None:
    decoder_type = registry.decoders.get(FileFormat(format)) if format else registry.match(source)
    if decoder_type is None:
        raise click.UsageError(f"Unsupported source format: '{format or source.suffix}'.")

    format = str(decoder_type.format)

    size = source.stat().st_size
    console = Console()
    options = Options(model=Options.Model(skeleton=True, animation=True))

    with decoder_type(source, options) as decoder:
        try:
            data = decoder.decode()

        except Exception as exception:
            position = getattr(exception, "offset", None)

            if position is None:
                position = decoder.io.tell()

            console.print("[bold red]Decode failed[/]")
            console.print(
                tables.failure(
                    source,
                    format,
                    size,
                    decoder_type.__name__,
                    decoder.data,
                    exception,
                    position,
                    parser(exception),
                )
            )
            raise click.exceptions.Exit(1)

    console.print(tables.content(source, format, size, decoder_type.__name__, data))
