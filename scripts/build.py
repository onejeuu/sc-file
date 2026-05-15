import os
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
    args: list[tuple[str, ...]] = [
        (ENTRYPOINT,),
        ("-i", FAVICON),
        ("--name", NAME),
        ("--specpath", SPECPATH),
        ("--additional-hooks-dir", HOOKS),
        ("--add-data", f"{FAVICON}:assets"),
        ("--add-data", f"{ASSETS}:assets"),
        ("--onefile",),
    ]

    if sha := os.environ.get("GITHUB_SHA"):
        commit = Path(SPECPATH) / "commit"
        commit.write_text(sha.strip())
        args.append(("--add-data", f"{commit}:."))

    PyInstaller.__main__.run([s for pair in args for s in pair])


if __name__ == "__main__":
    build()
