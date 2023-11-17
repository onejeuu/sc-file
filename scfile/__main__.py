from pathlib import Path

import click
from rich import print

from scfile.exceptions import ScFileException
from scfile.utils import convert


@click.command(no_args_is_help=True)
@click.argument(
    "file",
    type=click.Path(path_type=Path, exists=True, readable=True, dir_okay=False)
)
@click.option(
    "-O", "--output", nargs=1,
    help="Optional path to output (include new filename). Defaults to source path with new suffix.",
    type=click.Path(path_type=Path, exists=False, writable=True, dir_okay=False)
)
def main(file: Path, output: Path):
    try:
        convert.auto(file, output)

    except ScFileException as err:
        print(f"\n[b red]Error:[/] {err}")

    except Exception as err:
        print(f"\n[b red]Unknown Error:[/] {err}")

    except KeyboardInterrupt:
        print("\n\n[b yellow]Operation aborted.[/]")

    finally:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
