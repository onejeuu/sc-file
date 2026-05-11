from pathlib import Path

import PyInstaller.__main__


NAME = "scfile"

SCRIPTS = Path(__file__).parent.absolute()
ROOT = SCRIPTS.parent

ENTRYPOINT = str(ROOT / "scfile" / "__main__.py")
FAVICON = str(ROOT / "assets" / "scfile.ico")
ASSETS = str(ROOT / "scfile" / "gui" / "assets")
SPECPATH = str(ROOT / "build")
HOOKS = str(SCRIPTS / "hooks")


def build():
    PyInstaller.__main__.run(
        [
            ENTRYPOINT,
            "-i",
            FAVICON,
            "--name",
            NAME,
            "--specpath",
            SPECPATH,
            "--additional-hooks-dir",
            HOOKS,
            "--add-data",
            f"{FAVICON}:assets",
            "--add-data",
            f"{ASSETS}:assets",
            "--onefile",
        ]
    )


if __name__ == "__main__":
    build()
