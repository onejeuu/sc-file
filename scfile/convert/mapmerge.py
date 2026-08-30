"""Flat map merging operations."""

from collections.abc import Callable, Generator, Iterable, Mapping
from contextlib import contextmanager
from dataclasses import replace
from io import BytesIO
from pathlib import Path
from typing import Any, NamedTuple

from PIL import Image

from scfile import exceptions, formats, types
from scfile.options import Options

from . import paths
from .regions import Bounds, CancelCheck, Region, Size


PREFIX = "r."
MIN_TILE_SIZE = 7 * 1024
JPEG_QUALITY = 92
PNG_COMPRESSION = 6

type SaveOptions = Mapping[str, Any]
DEFAULT_SAVE: SaveOptions = {"format": "JPEG", "quality": JPEG_QUALITY}

type Tiles = dict[Region, Path]
type Progress = Callable[[Path], None] | None


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


def measure(
    tiles: Mapping[Region, Path],
    options: Options | None = None,
    cancelled: CancelCheck = None,
) -> Size:
    """Measure the output image without decoding tile pixels."""

    if not tiles:
        raise exceptions.ConversionError("No map tiles found.")

    options = options or Options()
    bounds = Bounds.parse(tiles)
    return bounds.size(_tile_size(tiles, options, cancelled))


def merge(
    source: types.SourceLike,
    output: types.SourceLike,
    options: Options | None = None,
    save: SaveOptions | None = None,
    cancelled: CancelCheck = None,
    progress: Progress = None,
) -> MergeResult:
    """Merge map tiles from one folder into an image."""

    output_path = Path(output)
    tiles = scan(source)
    if not tiles:
        raise exceptions.ConversionError("No map tiles found.", location=str(source))

    return render(tiles, output_path, options, save, cancelled, progress)


def render(
    tiles: Mapping[Region, Path],
    output: types.SourceLike,
    options: Options | None = None,
    save: SaveOptions | None = None,
    cancelled: CancelCheck = None,
    progress: Progress = None,
) -> MergeResult:
    """Merge normalized map tiles into an image."""

    output_path = Path(output)
    options = options or Options()
    save = DEFAULT_SAVE if save is None else save

    if not tiles:
        raise exceptions.ConversionError("No map tiles found.")

    tiles = dict(sorted(tiles.items()))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    decoder_options = replace(options, max_mipmaps=1)
    bounds = Bounds.parse(tiles)
    tile_size = _tile_size(tiles, options, cancelled)
    canvas_size = bounds.size(tile_size)
    canvas = Image.new("RGB", canvas_size)

    try:
        for key, path in tiles.items():
            if cancelled and cancelled():
                raise exceptions.MergeInterrupted()

            with _decode(path, decoder_options) as image:
                _paste(canvas, bounds, key, image, tile_size)

            if progress:
                progress(path)

        with paths.stage(output_path) as temporary:
            canvas.save(temporary, **save)

    finally:
        canvas.close()

    return MergeResult(output_path, len(tiles))


def _tile(path: Path) -> tuple[Region, Path] | None:
    if key := Region.parse(path.stem.removeprefix(PREFIX)):
        return key, path


def _tile_size(
    tiles: Mapping[Region, Path],
    options: Options,
    cancelled: CancelCheck,
) -> Size:
    metadata_options = replace(options, max_mipmaps=0)
    sizes: dict[Path, Size] = {}
    for path in tiles.values():
        if cancelled and cancelled():
            raise exceptions.MergeInterrupted()
        sizes[path] = _size(path, metadata_options)

    tile_size = min(sizes.values(), key=lambda size: size.width * size.height)
    for path, size in sizes.items():
        if size.width * tile_size.height != tile_size.width * size.height:
            raise exceptions.ConversionError(
                f"Map tile aspect ratio {size} does not match {tile_size}.",
                location=str(path),
            )

    return tile_size


def _size(path: Path, options: Options) -> Size:
    with formats.OlDecoder(path, options) as decoder:
        content = decoder.decode()

    size = Size(width=content.width, height=content.height)
    if size.width <= 0 or size.height <= 0:
        raise exceptions.ConversionError("Map tile has invalid size.", location=str(path))
    return size


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
    image: Image.Image,
    tile_size: Size,
) -> None:
    image_size = Size(width=image.width, height=image.height)
    if image_size == tile_size:
        canvas.paste(image, bounds.offset(key, tile_size))
        return

    with image.resize(tile_size, Image.Resampling.LANCZOS) as resized:
        canvas.paste(resized, bounds.offset(key, tile_size))
