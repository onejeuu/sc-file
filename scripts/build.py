import os
from pathlib import Path

import PyInstaller.__main__


NAME = "scfile"

SCRIPTS = Path(__file__).parent.absolute()
ROOT = SCRIPTS.parent

ENTRYPOINT = ROOT / "scfile" / "__main__.py"
FAVICON = ROOT / "assets" / "scfile.ico"
ASSETS = ROOT / "scfile" / "gui" / "assets"
SPECPATH = ROOT / "build"
COMMIT = SPECPATH / "commit"
HOOKS = SCRIPTS / "hooks"


def build():
    args: list[tuple[str, ...]] = [
        (str(ENTRYPOINT),),
        ("--name", NAME),
        ("-i", str(FAVICON)),
        ("--specpath", str(SPECPATH)),
        ("--additional-hooks-dir", str(HOOKS)),
        ("--add-data", f"{FAVICON}:assets"),
        ("--add-data", f"{ASSETS}:assets"),
        ("--onefile",),
    ]

    if sha := os.environ.get("GITHUB_SHA"):
        SPECPATH.mkdir(parents=True, exist_ok=True)
        COMMIT.write_text(sha.strip())
        args.append(("--add-data", f"{COMMIT}:."))

    PyInstaller.__main__.run([s for pair in args for s in pair])


if __name__ == "__main__":
    build()
