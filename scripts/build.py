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
        ]
    )


if __name__ == "__main__":
    build()
