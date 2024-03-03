from pathlib import Path

import PyInstaller.__main__


NAME = "scfile"

ROOT = Path(__file__).parent.absolute()
ENTRYPOINT = str(ROOT / "scfile" / "__main__.py")
ICON = str(ROOT / "assets" / "icon.ico")
SPECPATH = str(ROOT / "build")


def build():
    PyInstaller.__main__.run(
        [ENTRYPOINT, "-i", ICON, "--name", NAME, "--specpath", SPECPATH, "--onefile"]
    )
