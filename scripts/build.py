from pathlib import Path

import PyInstaller.__main__


NAME = "scfile"

ROOT = Path(__file__).parent.parent.absolute()

ENTRYPOINT = str(ROOT / "scfile" / "__main__.py")
ICON = str(ROOT / "assets" / "scfile.ico")
SPECPATH = str(ROOT / "build")


def build():
    PyInstaller.__main__.run(
        [
            ENTRYPOINT,
            "-i",
            ICON,
            "--name",
            NAME,
            "--specpath",
            SPECPATH,
            "--onefile",
            # Fix for rich library Unicode support in compiled executable
            # PyInstaller doesnt automatically detect these submodules
            "--hidden-import",
            "rich._unicode_data.unicode17-0-0",  # Unicode 17.0.0 data tables
            "--hidden-import",
            "rich._unicode_data",  # Unicode data module
            "--collect-data",
            "rich",  # Package data files
        ]
    )


if __name__ == "__main__":
    build()
