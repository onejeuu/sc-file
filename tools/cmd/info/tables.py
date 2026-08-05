from collections.abc import Iterable
from pathlib import Path

from rich.filesize import decimal
from rich.table import Table
from rich.text import Text

from scfile.core import (
    ArchiveContent,
    BaseContent,
    DocumentContent,
    ImageContent,
    ModelContent,
    RegionContent,
    TextureContent,
)
from scfile.structures.textures import CubemapTexture, DefaultTexture


Row = tuple[str, object]


def _size(value: int) -> str:
    formatted = decimal(value)
    return formatted if value < 1000 else f"{formatted} ({value:,} bytes)"


def _table(rows: Iterable[Row], error: bool = False) -> Table:
    table = Table(
        box=None,
        show_header=False,
    )
    table.add_column(style="red" if error else "cyan")
    table.add_column()

    for field, value in rows:
        text = Text(str(value))
        if error and field == "Error":
            text.stylize("bold red")
        table.add_row(field, text)

    return table


def content(source: Path, format: str, size: int, decoder: str, data: BaseContent) -> Table:
    rows: list[Row] = [
        ("Path", source),
        ("Format", format),
        ("Size", _size(size)),
        ("Decoder", decoder),
        ("Content", type(data).__name__),
    ]

    match data:
        case ModelContent():
            rows.extend(_model(data))

        case TextureContent():
            rows.extend(_texture(data))

        case ImageContent():
            rows.append(("Image", _size(len(data.image))))

        case ArchiveContent():
            rows.extend(
                (
                    ("Entries", len(data.entries)),
                    ("Data", decimal(sum(len(payload) for _, payload in data.entries))),
                )
            )
        case DocumentContent():
            rows.extend(_document(data))

        case RegionContent():
            rows.extend(
                (
                    ("Chunks", len(data.chunks)),
                    ("Slots", sum(offset != 0 for offset in data.sector_offsets)),
                )
            )

    return _table(rows)


def failure(
    source: Path,
    format: str,
    size: int,
    decoder: str,
    data: BaseContent,
    exception: Exception,
    position: int,
    parser: tuple[str, str, str] | None,
) -> Table:
    offset = f"{position:,} (0x{position:X}"
    if size:
        offset += f", {position / size:.2%}"
    offset += ")"

    rows: list[Row] = [
        ("Path", source),
        ("Format", format),
        ("Size", _size(size)),
        ("Decoder", decoder),
        ("Content", type(data).__name__),
        ("Error", f"{type(exception).__name__}: {exception}"),
        ("Offset", offset),
    ]

    if parser is not None:
        name, code, location = parser
        rows.extend(
            (
                ("Parser", name),
                ("Code", code),
                ("Source", location),
            )
        )

    return _table(rows, error=True)


def _model(data: ModelContent) -> list[Row]:
    scene = data.scene
    flags = ", ".join(feature.name for feature, enabled in data.flags.items() if enabled) or "-"

    return [
        ("Version", data.version),
        ("Flags", flags),
        ("Meshes", len(scene.meshes)),
        ("Vertices", f"{scene.total_vertices:,}"),
        ("Polygons", f"{scene.total_polygons:,}"),
        ("Bones", len(scene.skeleton.bones)),
        ("Roots", len(scene.skeleton.roots)),
        ("Clips", len(scene.animation.clips)),
        ("Frames", f"{sum(clip.frames for clip in scene.animation.clips):,}"),
    ]


def _texture(data: TextureContent) -> list[Row]:
    match data.texture:
        case DefaultTexture():
            kind = "DEFAULT"
            faces = 1

        case CubemapTexture() as texture:
            kind = "CUBEMAP"
            faces = len(texture.faces)

        case _:
            kind = type(data.texture).__name__
            faces = 0

    return [
        ("Width", data.width),
        ("Height", data.height),
        ("Kind", kind),
        ("Format", data.format.decode(errors="replace")),
        ("FourCC", data.fourcc.decode(errors="replace")),
        ("Mipmaps", data.mipmap_count),
        ("Faces", faces),
        ("Image", _size(len(data.texture.image))),
        ("Path Hash", data.path_hash.decode(errors="replace") or "-"),
    ]


def _document(data: DocumentContent) -> list[Row]:
    value = data.value
    rows: list[Row] = [("Root", type(value).__name__)]
    if isinstance(value, bytes | list | dict):
        rows.append(("Entries", len(value)))
    return rows
