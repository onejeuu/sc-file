from pathlib import Path
from argparse import ArgumentParser

from scfile import exceptions as exc
from scfile.utils import convert


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
        convert.auto(source, output)

    except exc.SourceFileNotFound as err:
        print("File", err, "not found (not exists).")

    except exc.UnsupportedFormat as err:
        print("File", err, "is unsupported.")

    except exc.InvalidSignature as err:
        print(
            "File", err, "has invalid signature."
            "(file suffix does not match file type)"
        )

    except exc.FileIsEmpty as err:
        print("Input file", err, "is empty.")

    except exc.ReaderError as err:
        print("Reading file error:", err)

    except exc.OlUnsupportedFormat as err:
        print("Texture has unsupported format:", err)

    except exc.McsaUnsupportedVersion as err:
        print("Model has unsupported version:", err)

    except exc.McsaUnsupportedFlags as err:
        print("Model has unsupported flags:", err)

    except exc.McsaUnsupportedLinkCount as err:
        print("Model has unsupported bones link count:", err)

    except exc.McsaFileError | exc.OlFileError as err:
        print("File converting error:", err)

    except exc.ScFileException as err:
        print("ScFile error:", err)

    except Exception as err:
        print("Unknown error:", err)


def noargs(parser: ArgumentParser):
    parser.print_help()
    print()
    input("Press Enter to exit...")


def main():
    parser = get_parser()
    args = parser.parse_args()

    output = args.output

    if source := args.source:
        run(source, output)
        return

    noargs(parser)


if __name__ == "__main__":
    main()
