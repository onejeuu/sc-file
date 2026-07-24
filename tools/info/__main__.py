from pathlib import Path

import click
from rich.console import Console

from scfile.convert import decoders, detect
from scfile.core import FileDecoder, Options
from tools.info import tables


DECODERS = decoders()
CONTEXT_SIZE = 16


def context(decoder: FileDecoder, position: int) -> tuple[bytes, bytes]:
    position = min(max(position, 0), decoder.size())
    decoder.seek(max(0, position - CONTEXT_SIZE))
    before = decoder.read(min(CONTEXT_SIZE, position))
    decoder.seek(position)
    after = decoder.read(CONTEXT_SIZE)
    return before, after


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

            before, after = context(decoder, position)
            console.print("[bold red]Decode failed[/]")
            console.print(
                tables.failure(
                    source,
                    format,
                    size,
                    decoder_type.__name__,
                    type(decoder.data).__name__,
                    exception,
                    position,
                    before,
                    after,
                )
            )
            raise click.exceptions.Exit(1)

    console.print(tables.content(source, format, size, decoder_type.__name__, data))


if __name__ == "__main__":
    main()
