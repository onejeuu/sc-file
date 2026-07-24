"""Serve English and Russian documentation."""

import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
LOCALE = ROOT / "locale"
BUILD = ROOT / "_build"

HOST = "127.0.0.1"
SERVERS = (
    ("English", "en", 8000),
    ("Russian", "ru", 8001),
)


def command(language: str, port: int) -> list[str]:
    result = [
        sys.executable,
        "-m",
        "sphinx_autobuild",
        "--host",
        HOST,
        "--port",
        str(port),
        "-D",
        f"language={language}",
    ]

    if language == "ru":
        result.extend(("--watch", str(LOCALE)))

    result.extend((str(SOURCE), str(BUILD / language)))
    return result


def main() -> None:
    for name, _, port in SERVERS:
        print(f"{name}: http://{HOST}:{port}")

    processes = [subprocess.Popen(command(language, port)) for _, language, port in SERVERS]
    exit_code = 0

    try:
        while all(process.poll() is None for process in processes):
            time.sleep(0.2)

        exit_code = next((process.returncode for process in processes if process.returncode), 0)

    except KeyboardInterrupt:
        pass

    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()

        for process in processes:
            try:
                process.wait(timeout=5)

            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
