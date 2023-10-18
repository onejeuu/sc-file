import PyInstaller.__main__
from pathlib import Path


ROOT = Path(__file__).parent.absolute()
ENTRYPOINT = str(ROOT / "scfile" / "__main__.py")
ICON = str(ROOT / "assets" / "icon.ico")


def build():
    PyInstaller.__main__.run([
        ENTRYPOINT,
        "-i", ICON,
        "--name", "SCF",
        "--specpath", "build",
        "--onefile"
    ])
