from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from itertools import islice
from pathlib import Path
from typing import Iterator

from rich.console import Console

from scfile.consts import SUPPORTED_NBT
from scfile.convert import detect
from scfile.core import Options
from scfile.utils.files import walk
from tools.audit.config import DECODERS, Config
from tools.audit.types import Asset, Error, Result


def _decode(asset: Asset, config: Config, options: Options) -> Result:
    try:
        with DECODERS[asset.format](asset.path, options) as decoder:
            decoder.decode()

    except Exception as error:
        relative = asset.path.relative_to(config.path).as_posix()
        message = str(error).replace(str(asset.path), relative)
        return Result(
            format=asset.format,
            error=Error(
                path=relative,
                error=f"{type(error).__name__}: {message}",
            ),
        )

    return Result(format=asset.format)


def find_assets(config: Config, console: Console) -> list[Asset]:
    assets: list[Asset] = []
    whitelist = [f".{format}" for format in config.formats if format != "nbt"]
    if "nbt" in config.formats:
        whitelist.extend(SUPPORTED_NBT)

    with console.status("Searching... 0 files") as status:
        for entry in walk([config.path], whitelist):
            if entry.relpath.lower().replace("\\", "/") in config.exclude:
                continue

            path = Path(entry.path)
            format = detect.format(path)
            if format not in config.formats:
                continue
            assets.append(Asset(path=path, format=format))
            status.update(f"Searching... {len(assets)} files")

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
