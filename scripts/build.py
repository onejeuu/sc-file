from pathlib import Path

import PyInstaller.__main__


NAME = "scfile"

SCRIPTS = Path(__file__).parent.absolute()
ROOT = SCRIPTS.parent

ENTRYPOINT = str(ROOT / "scfile" / "__main__.py")
ICON = str(ROOT / "assets" / "scfile.ico")
SPECPATH = str(ROOT / "build")
HOOKS = str(SCRIPTS / "hooks")


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
            "--additional-hooks-dir",
            HOOKS,
            "--onefile",
            # Add icon to binary data
            "--add-data",
            f"{ICON}:assets",
        ]
    )


if __name__ == "__main__":
    build()
