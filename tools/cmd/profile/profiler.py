import cProfile
import pstats
from collections.abc import Callable
from pathlib import Path
from time import perf_counter

from scfile.options import Options
from scfile.core import FileDecoder, FileEncoder


def decode(
    source: Path,
    decoder: type[FileDecoder],
    options: Options,
) -> None:
    with decoder(source, options) as src:
        src.decode()


def convert(
    source: Path,
    decoder: type[FileDecoder],
    encoder: type[FileEncoder],
    options: Options,
) -> None:
    with decoder(source, options) as src:
        with src.convert_to(encoder) as out:
            out.encode()


def run(
    operation: Callable[[], None],
    count: int,
    output: Path,
) -> tuple[pstats.Stats, float, int]:
    profile = cProfile.Profile()

    with profile:
        operation()

    started = perf_counter()
    for _ in range(count):
        operation()
    elapsed = perf_counter() - started

    output.parent.mkdir(parents=True, exist_ok=True)
    profile.dump_stats(output)
    calls = sum(item.callcount for item in profile.getstats())
    return pstats.Stats(profile), elapsed, calls
