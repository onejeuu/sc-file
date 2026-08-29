"""Flat map merging operations."""

from collections.abc import Generator, Iterable, Mapping
from contextlib import contextmanager
from dataclasses import replace
from io import BytesIO
from pathlib import Path
from typing import NamedTuple

from PIL import Image

from scfile import exceptions, formats, types
from scfile.options import Options

from . import paths
from .regions import Bounds, CancelCheck, Region, Size


PREFIX = "r."
MIN_TILE_SIZE = 7 * 1024
JPEG_QUALITY = 95
OUTPUT_FORMATS = {
    suffix: image_format
    for suffix, image_format in Image.registered_extensions().items()
    if image_format in Image.SAVE
}

type Tiles = dict[Region, Path]


class MergeResult(NamedTuple):
    output: Path
    tiles: int


def scan(
    source: types.SourceLike,
) -> Tiles:
    """Find usable map tiles directly inside a folder."""

    suffix = formats.OlDecoder.suffix()
    paths = filter(lambda path: path.is_file() and path.suffix.lower() == suffix, Path(source).iterdir())
    paths = filter(lambda path: path.stat().st_size >= MIN_TILE_SIZE, paths)
    tiles = filter(None, map(_tile, paths))
    return dict(sorted(tiles))


def collect(
    sources: Iterable[types.SourceLike],
) -> Tiles:
    """Collect map tiles from ordered source folders."""

    tiles: Tiles = {}
    for source in sources:
        tiles.update(scan(source))
    return dict(sorted(tiles.items()))


def merge(
    source: types.SourceLike,
    output: types.SourceLike,
    options: Options | None = None,
    cancelled: CancelCheck = None,
) -> MergeResult:
    """Merge map tiles from one folder into an image."""

    output_path = Path(output)
    tiles = scan(source)
    if not tiles:
        raise exceptions.ConversionError("No map tiles found.", location=str(source))

    return render(tiles, output_path, options, cancelled)


def render(
    tiles: Mapping[Region, Path],
    output: types.SourceLike,
    options: Options | None = None,
    cancelled: CancelCheck = None,
) -> MergeResult:
    """Merge normalized map tiles into an image."""

    output_path = Path(output)
    image_format = OUTPUT_FORMATS.get(output_path.suffix.lower())
    if image_format is None:
        raise exceptions.ConversionError("Unsupported map output format.", location=str(output_path))
    options = options or Options()

    if not tiles:
        raise exceptions.ConversionError("No map tiles found.")

    tiles = dict(sorted(tiles.items()))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    decoder_options = replace(options, max_mipmaps=1)
    if cancelled and cancelled():
        raise exceptions.MergeInterrupted()

    with _decode(next(iter(tiles.values())), decoder_options) as image:
        tile_size = Size(width=image.width, height=image.height)

    bounds = Bounds.parse(tiles)
    canvas_size = bounds.size(tile_size)
    canvas = Image.new("RGB", canvas_size)

    try:
        for key, path in tiles.items():
            if cancelled and cancelled():
                raise exceptions.MergeInterrupted()

            with _decode(path, decoder_options) as image:
                _paste(canvas, bounds, key, path, image, tile_size)

        with paths.stage(output_path) as temporary:
            save_options = {"quality": JPEG_QUALITY} if image_format == "JPEG" else {}
            canvas.save(temporary, format=image_format, **save_options)

    finally:
        canvas.close()

    return MergeResult(output_path, len(tiles))


def _tile(path: Path) -> tuple[Region, Path] | None:
    if key := Region.parse(path.stem.removeprefix(PREFIX)):
        return key, path


@contextmanager
def _decode(path: Path, options: Options) -> Generator[Image.Image, None, None]:
    with formats.OlDecoder(path, options) as ol:
        dds = ol.convert(formats.DdsEncoder)

    with Image.open(BytesIO(dds)) as decoded:
        with decoded.convert("RGB") as image:
            yield image


def _paste(
    canvas: Image.Image,
    bounds: Bounds,
    key: Region,
    path: Path,
    image: Image.Image,
    tile_size: Size,
) -> None:
    image_size = Size(width=image.width, height=image.height)
    if image_size != tile_size:
        raise exceptions.ConversionError(
            f"Map tile size {image_size} does not match {tile_size}.",
            location=str(path),
        )

    canvas.paste(image, bounds.offset(key, tile_size))
