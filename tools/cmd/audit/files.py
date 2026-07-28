import os
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from itertools import islice
from typing import Iterator

from rich.console import Console

from scfile.consts import SUPPORTED_NBT
from scfile.convert import detect
from scfile.core import Options
from scfile.exceptions import EmptyFileError
from scfile.utils.files import walk
from tools.cmd.audit import stats
from tools.cmd.audit.config import Config
from tools.cmd.audit.consts import DECODERS
from tools.cmd.audit.types import Asset, Error, Result


IGNORED_EXCEPTIONS = (EmptyFileError,)


def _decode(asset: Asset, config: Config, options: Options) -> Result:
    try:
        with DECODERS[asset.format](asset.path, options) as decoder:
            content = decoder.decode(seek=False)

    except IGNORED_EXCEPTIONS:
        return Result(format=asset.format)

    except Exception as error:
        relative = os.path.relpath(asset.path, config.path).replace("\\", "/")
        return Result(
            format=asset.format,
            error=Error(
                path=relative,
                error=f"{type(error).__name__}: {error}",
            ),
        )

    records = stats.records(asset, content, config.path, config.animation) if config.stats else None
    return Result(format=asset.format, records=records)


def find_assets(config: Config, console: Console) -> list[Asset]:
    assets: list[Asset] = []
    formats = set(config.formats)
    whitelist = [f".{format}" for format in formats if format != "nbt"]
    if "nbt" in formats:
        whitelist.extend(SUPPORTED_NBT)

    with console.status("Searching... 0 files") as status:
        updated = time.monotonic()

        for entry in walk([config.path], whitelist):
            if entry.path.lower().replace("\\", "/").endswith(config.exclude):
                continue

            format = detect.format(entry.path)
            if format not in formats:
                continue

            assets.append(Asset(path=entry.path, format=format))

            now = time.monotonic()
            if now - updated >= 0.1:
                status.update(f"Searching... {len(assets)} files")
                updated = now

    return assets


def decode_assets(assets: list[Asset], config: Config) -> Iterator[Result]:
    options = Options(skeleton=config.animation, animation=config.animation)

    if config.workers == 0:
        for asset in assets:
            yield _decode(asset, config, options)
        return

    iterator = iter(assets)
    limit = max(config.workers * 2, 1)

    with ThreadPoolExecutor(max_workers=config.workers) as executor:
        pending: set[Future[Result]] = {
            executor.submit(_decode, asset, config, options) for asset in islice(iterator, limit)
        }

        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            pending.update(executor.submit(_decode, asset, config, options) for asset in islice(iterator, len(done)))
            for future in done:
                yield future.result()
