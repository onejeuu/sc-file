import os
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__
from rich import print

from scfile import __version__


NAME = "scfile"

SCRIPTS = Path(__file__).parent.absolute()
ROOT = SCRIPTS.parent

ENTRYPOINT = ROOT / "scfile" / "__main__.py"
FAVICON = ROOT / "assets" / "scfile.ico"
ASSETS = ROOT / "scfile" / "app" / "gui" / "assets"
NOTICE = ROOT / "NOTICE"

HOOKS = SCRIPTS / "hooks"
ISS = SCRIPTS / "installer.iss"

SPECPATH = ROOT / "build"
COMMIT = SPECPATH / "commit"

DISTPATH = ROOT / "dist"
SETUP = DISTPATH / "setup"


def build(*options: tuple[str, ...]):
    args: list[tuple[str, ...]] = [
        (str(ENTRYPOINT),),
        ("--name", NAME),
        ("-i", str(FAVICON)),
        ("--specpath", str(SPECPATH)),
        ("--additional-hooks-dir", str(HOOKS)),
        ("--add-data", f"{FAVICON}:assets"),
        ("--add-data", f"{ASSETS}:assets"),
        ("--add-data", f"{NOTICE}:."),
    ]

    if sha := os.environ.get("GITHUB_SHA"):
        SPECPATH.mkdir(parents=True, exist_ok=True)
        COMMIT.write_text(sha.strip())
        args.append(("--add-data", f"{COMMIT}:."))

    args.extend(options)
    PyInstaller.__main__.run([s for pair in args for s in pair])


def setup():
    build(
        ("--onedir",),
        ("--contents-directory", "bin"),
        ("--distpath", str(SETUP)),
        ("--noconfirm",),
    )

    try:
        subprocess.run(["iscc", f"/DAppVersion={__version__}", str(ISS)], check=True)

    except FileNotFoundError:
        print()
        print("[red]Inno Setup was not found. Install it and run script again:[/red]")
        print("  https://jrsoftware.org/isdl.php")
        sys.exit(1)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup()
    else:
        build(("--onefile",))
