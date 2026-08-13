import cProfile
import pstats
from collections.abc import Callable
from pathlib import Path
from time import perf_counter

from scfile.core import Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import Options
from scfile.structures.content import BaseContent


def decode[
    ContentType: BaseContent,
    ReaderType: StructReader,
](
    source: Path,
    decoder: type[Decoder[ContentType, ReaderType]],
    options: Options,
) -> None:
    with decoder(source, options) as src:
        src.decode()


def convert[
    ContentType: BaseContent,
    ReaderType: StructReader,
    WriterType: StructWriter,
](
    source: Path,
    decoder: type[Decoder[ContentType, ReaderType]],
    encoder: type[Encoder[ContentType, WriterType]],
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
