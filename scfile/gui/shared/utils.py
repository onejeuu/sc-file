import sys
from pathlib import Path


def get_resource(path: Path | str) -> Path:
    meipass = getattr(sys, "_MEIPASS", None)

    if meipass:
        return Path(meipass) / path

    base = Path(__file__).parent.parent.absolute()
    return base / path
