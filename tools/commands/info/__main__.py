import linecache
import traceback
from pathlib import Path

import click
from rich.console import Console

from scfile.convert import decoders, detect
from scfile.core import Options
from tools.commands.info import tables
from tools.paths import ROOT


FORMATS = ROOT.parent / "scfile" / "formats"
DECODERS = decoders()


def parser(exception: Exception) -> tuple[str, str, str] | None:
    found = None
    fallback = None

    for frame, lineno in traceback.walk_tb(exception.__traceback__):
        path = Path(frame.f_code.co_filename).resolve()
        if not path.is_relative_to(FORMATS):
            continue

        item = (
            frame.f_code.co_name,
            linecache.getline(str(path), lineno).strip(),
            f"{path.relative_to(ROOT.parent).as_posix()}:{lineno}",
        )
        fallback = item

        if item[0] == "parse" or item[0].startswith("_parse"):
            found = item

    return found or fallback


@click.command()
@click.argument(
    "SOURCE",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
def main(source: Path) -> None:
    format = detect.format(source)
    decoder_type = DECODERS.get(format)
    if decoder_type is None:
        raise click.UsageError(f"Unsupported source format: '{format}'.")

    size = source.stat().st_size
    console = Console()
    options = Options(skeleton=True, animation=True)

    with decoder_type(source, options) as decoder:
        try:
            data = decoder.decode(seek=False)

        except Exception as exception:
            position = getattr(exception, "position", None)

            if position is None:
                position = decoder.tell()

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


if __name__ == "__main__":
    main()
