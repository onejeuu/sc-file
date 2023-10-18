from pathlib import Path
from argparse import ArgumentParser

from scfile.utils import func


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="SCF",
        description="Converting encrypted sc game files."
    )

    parser.add_argument(
        "--source",
        "-S",
        type=Path,
        metavar="FILE",
        help="Path to encrypted game file."
    )

    parser.add_argument(
        "--output",
        "-O",
        type=Path,
        metavar="FILE",
        help=(
            "Optional path to output (include new filename). "
            "Defaults to source path with new suffix."
        )
    )

    return parser


def run(source: Path, output: Path):
    try:
        func.auto(source, output)

    except Exception as err:
        print("Error:", err)


def pause():
    print()
    input("Press Enter to exit...")


def main():
    parser = get_parser()
    args = parser.parse_args()

    output = args.output

    if source := args.source:
        run(source, output)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
    pause()
