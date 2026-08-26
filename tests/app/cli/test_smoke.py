from pathlib import Path
from shutil import copy2

import click
import pytest

from scfile.app.cli import run
from scfile.app.enums import OutputLayout
from scfile.app.formats import model_formats
from scfile.enums import FileFormat
from scfile.formats import registry


ASSETS = Path(__file__).parents[2] / "assets"
FORMATS = ASSETS / "formats"
MODEL_SOURCE = FORMATS / "models" / "source" / "model_v15.mcsb"
ANIMATION_SOURCE = FORMATS / "models" / "source" / "animation.mcvd"
LIBRARY_SOURCE = FORMATS / "models" / "source" / "library.mcal"
REGION_SOURCE = FORMATS / "region" / "source"
DOCUMENT_SOURCE = FORMATS / "document" / "source" / "document.nbt"
IMAGE_SOURCE = FORMATS / "image" / "source" / "screen.mic"
TEXTURE_SOURCE = FORMATS / "textures" / "source" / "texture_dxt1.ol"

SOURCES = tuple(sorted(path for path in FORMATS.glob("**/source/*") if path.is_file()))
BROKEN_SOURCES = tuple(sorted(path for path in (ASSETS / "invalid").iterdir() if path.is_file()))
MODEL_SOURCES = tuple(
    source for source in SOURCES if source.suffix.lower() in {".efkmodel", ".mcal", ".mcsa", ".mcsb", ".mcvd"}
)
NBT_SOURCES = tuple(sorted((FORMATS / "document" / "source").iterdir()))
NBT_NAMES = tuple(sorted(registry.aliases[FileFormat.NBT]))


def _launch(args: list[str]) -> None:
    try:
        run(args)
    except (click.ClickException, click.exceptions.Exit):
        pass


def _source_id(path: Path) -> str:
    return path.relative_to(ASSETS).as_posix()


def _copy(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)
    return destination


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["--version"],
        ["convert", "--help"],
        ["animate", "--help"],
        ["animate", "arms", "--help"],
        ["animate", "face", "--help"],
        ["animate", "body", "--help"],
        ["mapcache", "--help"],
    ],
)
def test_cli_help_smoke(args: list[str]) -> None:
    _launch(args)


@pytest.mark.parametrize("source", (*SOURCES, *BROKEN_SOURCES), ids=_source_id)
def test_convert_every_fixture_smoke(source: Path, tmp_path: Path) -> None:
    _launch(["convert", str(source), "-O", str(tmp_path), "-W", "1"])


@pytest.mark.parametrize("layout", OutputLayout)
def test_convert_layout_smoke(layout: OutputLayout, tmp_path: Path) -> None:
    _launch(["convert", str(FORMATS), "-O", str(tmp_path), "--layout", layout, "-W", "1"])


@pytest.mark.parametrize("format", registry.decoders, ids=str)
def test_convert_filter_smoke(format: str, tmp_path: Path) -> None:
    _launch(["convert", str(FORMATS), "-O", str(tmp_path), "-I", format, "-W", "1"])


@pytest.mark.parametrize("source", MODEL_SOURCES, ids=_source_id)
@pytest.mark.parametrize("format", model_formats(), ids=str)
@pytest.mark.parametrize(("skeleton", "animation"), ((False, False), (True, False), (False, True), (True, True)))
def test_convert_model_option_smoke(
    source: Path,
    format: FileFormat,
    skeleton: bool,
    animation: bool,
    tmp_path: Path,
) -> None:
    args = ["convert", str(source), "-O", str(tmp_path), "-F", format, "-W", "1"]
    if skeleton:
        args.append("--skeleton")
    if animation:
        args.append("--animation")
    _launch(args)


@pytest.mark.parametrize("layout", OutputLayout)
@pytest.mark.parametrize("on_conflict", ("replace", "rename", "skip"))
def test_convert_existing_conflict_smoke(
    layout: OutputLayout,
    on_conflict: str,
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "document.json").touch()

    _launch(
        [
            "convert",
            str(FORMATS / "document" / "source" / "document.nbt"),
            "-O",
            str(output),
            "--layout",
            layout,
            "--on-conflict",
            on_conflict,
            "-W",
            "1",
        ]
    )


def test_convert_default_output_smoke(tmp_path: Path) -> None:
    source = tmp_path / MODEL_SOURCE.name
    copy2(MODEL_SOURCE, source)

    _launch(["convert", str(source), "--skeleton", "--animation", "-W", "1"])


@pytest.mark.parametrize("output_name", ("output", "result.json"))
def test_convert_output_path_smoke(output_name: str, tmp_path: Path) -> None:
    _launch(["convert", str(DOCUMENT_SOURCE), "-O", str(tmp_path / output_name), "-W", "1"])


@pytest.mark.parametrize("workers", ("0", "1", "2"))
def test_convert_workers_smoke(workers: str, tmp_path: Path) -> None:
    _launch(
        [
            "convert",
            str(FORMATS / "document" / "source"),
            str(FORMATS / "image" / "source"),
            str(FORMATS / "textures" / "source"),
            "-O",
            str(tmp_path),
            "-W",
            workers,
            "--verbose",
        ]
    )


@pytest.mark.parametrize("formats", (("nbt", "mic"), ("texarr", "mdat")))
def test_convert_multiple_filters_smoke(formats: tuple[str, ...], tmp_path: Path) -> None:
    args = ["convert", str(FORMATS), "-O", str(tmp_path), "-W", "1"]
    for format in formats:
        args.extend(("-I", format))
    _launch(args)


@pytest.mark.parametrize("source", NBT_SOURCES, ids=_source_id)
@pytest.mark.parametrize("name", NBT_NAMES)
def test_convert_nbt_alias_smoke(source: Path, name: str, tmp_path: Path) -> None:
    input_path = _copy(source, tmp_path / "source" / name)
    _launch(["convert", str(input_path), "-O", str(tmp_path / "output"), "-I", "nbt", "-W", "1"])


def _convert_shape(kind: str, tmp_path: Path) -> tuple[list[Path], Path]:
    source = tmp_path / "source"
    output = tmp_path / "output"

    match kind:
        case "file":
            return [_copy(DOCUMENT_SOURCE, source / "document.nbt")], output
        case "directory":
            _copy(DOCUMENT_SOURCE, source / "document.nbt")
            _copy(IMAGE_SOURCE, source / "screen.mic")
            return [source], output
        case "nested":
            _copy(DOCUMENT_SOURCE, source / "documents" / "document.nbt")
            _copy(IMAGE_SOURCE, source / "images" / "screen.mic")
            _copy(TEXTURE_SOURCE, source / "textures" / "texture.ol")
            return [source], output
        case "multiple":
            document = _copy(DOCUMENT_SOURCE, source / "document.nbt")
            image = _copy(IMAGE_SOURCE, source / "nested" / "screen.mic")
            return [document, image], output
        case "duplicate":
            document = _copy(DOCUMENT_SOURCE, source / "document.nbt")
            return [document, document], output
        case "parent-and-child":
            nested = source / "nested"
            _copy(DOCUMENT_SOURCE, source / "document.nbt")
            _copy(IMAGE_SOURCE, nested / "screen.mic")
            return [source, nested], output
        case "empty":
            source.mkdir()
            return [source], output
        case "missing":
            return [source / "missing.nbt"], output
        case "unsupported":
            return [_copy(ASSETS / "invalid" / "unknown.xyz", source / "unknown.xyz")], output
        case "mixed":
            _copy(DOCUMENT_SOURCE, source / "document.nbt")
            _copy(IMAGE_SOURCE, source / "nested" / "screen.mic")
            _copy(ASSETS / "invalid" / "broken.ol", source / "nested" / "broken.ol")
            _copy(ASSETS / "invalid" / "unknown.xyz", source / "unknown.xyz")
            return [source], output
        case "output-inside-source":
            _copy(DOCUMENT_SOURCE, source / "document.nbt")
            _copy(IMAGE_SOURCE, source / "nested" / "screen.mic")
            return [source], source / "output"

    raise ValueError(kind)


@pytest.mark.parametrize(
    "kind",
    (
        "file",
        "directory",
        "nested",
        "multiple",
        "duplicate",
        "parent-and-child",
        "empty",
        "missing",
        "unsupported",
        "mixed",
        "output-inside-source",
    ),
)
@pytest.mark.parametrize("layout", OutputLayout)
def test_convert_source_shape_smoke(kind: str, layout: OutputLayout, tmp_path: Path) -> None:
    sources, output = _convert_shape(kind, tmp_path)
    _launch(
        [
            "convert",
            *(str(source) for source in sources),
            "-O",
            str(output),
            "--layout",
            layout,
            "-W",
            "2",
        ]
    )


def _collision_sources(kind: str, tmp_path: Path) -> list[Path]:
    match kind:
        case "same-directory":
            source = tmp_path / "source"
            _copy(MODEL_SOURCE, source / "model.mcsb")
            _copy(FORMATS / "models" / "source" / "model_v15.mcsa", source / "model.mcsa")
            return [source]
        case "separate-roots":
            left = _copy(DOCUMENT_SOURCE, tmp_path / "left" / "document.nbt")
            right = _copy(DOCUMENT_SOURCE, tmp_path / "right" / "document.nbt")
            return [left.parent, right.parent]
        case "same-relative-path":
            left = _copy(DOCUMENT_SOURCE, tmp_path / "left" / "documents" / "document.nbt")
            right = _copy(DOCUMENT_SOURCE, tmp_path / "right" / "documents" / "document.nbt")
            return [left.parent.parent, right.parent.parent]

    raise ValueError(kind)


@pytest.mark.parametrize("kind", ("same-directory", "separate-roots", "same-relative-path"))
@pytest.mark.parametrize("layout", OutputLayout)
@pytest.mark.parametrize("on_conflict", ("replace", "rename", "skip"))
def test_convert_source_collision_smoke(
    kind: str,
    layout: OutputLayout,
    on_conflict: str,
    tmp_path: Path,
) -> None:
    sources = _collision_sources(kind, tmp_path)
    _launch(
        [
            "convert",
            *(str(source) for source in sources),
            "-O",
            str(tmp_path / "output"),
            "-F",
            "obj",
            "--layout",
            layout,
            "--on-conflict",
            on_conflict,
            "-W",
            "2",
        ]
    )


def test_convert_failed_collision_smoke(tmp_path: Path) -> None:
    left = _copy(ASSETS / "invalid" / "counts.mcsb", tmp_path / "left" / "model.mcsb")
    right = _copy(MODEL_SOURCE, tmp_path / "right" / "model.mcsb")
    _launch(
        [
            "convert",
            str(left.parent),
            str(right.parent),
            "-O",
            str(tmp_path / "output"),
            "-F",
            "obj",
            "--layout",
            "dump",
            "-W",
            "2",
        ]
    )


def test_convert_relative_path_smoke(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = _copy(DOCUMENT_SOURCE, tmp_path / "вход с пробелом" / "prefs")
    monkeypatch.chdir(tmp_path)

    _launch(["convert", str(source.relative_to(tmp_path)), "-O", "выход с пробелом", "-I", "nbt", "-W", "1"])


@pytest.mark.parametrize(
    ("kind", "hands", "raw", "output_kind"),
    [
        ("arms", False, False, "file"),
        ("arms", True, False, "directory"),
        ("face", False, False, "file"),
        ("face", False, False, "directory"),
        ("body", False, False, "file"),
        ("body", False, True, "directory"),
    ],
)
def test_animate_smoke(
    kind: str,
    hands: bool,
    raw: bool,
    output_kind: str,
    tmp_path: Path,
) -> None:
    animation_source = LIBRARY_SOURCE if kind == "body" else ANIMATION_SOURCE
    animation = _copy(animation_source, tmp_path / animation_source.name)
    model = _copy(MODEL_SOURCE, tmp_path / "model.mcsb")
    args = ["animate", kind, str(animation), str(model)]
    if hands:
        args.append(str(_copy(MODEL_SOURCE, tmp_path / "hands.mcsb")))
    if raw:
        args.append("--raw")
    output = tmp_path / ("output" if output_kind == "directory" else "animation.glb")
    _launch([*args, "-O", str(output)])


@pytest.mark.parametrize("kind", ("arms", "face", "body"))
def test_animate_default_output_smoke(kind: str, tmp_path: Path) -> None:
    animation_source = LIBRARY_SOURCE if kind == "body" else ANIMATION_SOURCE
    animation = _copy(animation_source, tmp_path / animation_source.name)
    model = _copy(MODEL_SOURCE, tmp_path / "model.mcsb")
    _launch(["animate", kind, str(animation), str(model)])


@pytest.mark.parametrize("kind", ("arms", "face", "body"))
def test_animate_existing_output_smoke(kind: str, tmp_path: Path) -> None:
    animation_source = LIBRARY_SOURCE if kind == "body" else ANIMATION_SOURCE
    animation = _copy(animation_source, tmp_path / animation_source.name)
    model = _copy(MODEL_SOURCE, tmp_path / "model.mcsb")
    output = tmp_path / "animation.glb"
    output.write_bytes(b"existing")
    _launch(["animate", kind, str(animation), str(model), "-O", str(output)])


@pytest.mark.parametrize("kind", ("arms", "face", "body"))
def test_animate_broken_model_smoke(kind: str, tmp_path: Path) -> None:
    animation_source = LIBRARY_SOURCE if kind == "body" else ANIMATION_SOURCE
    animation = _copy(animation_source, tmp_path / animation_source.name)
    model = _copy(ASSETS / "invalid" / "counts.mcsb", tmp_path / "model.mcsb")
    _launch(["animate", kind, str(animation), str(model), "-O", str(tmp_path / "animation.glb")])


def _mapcache_sources(tmp_path: Path) -> Path:
    source = tmp_path / "mapcache"
    _copy(REGION_SOURCE / "r.0.0.mdat", source / "r.0.0.mdat")
    _copy(REGION_SOURCE / "r.0.0.mdat", source / "nested" / "reg.1.-1.mdat")
    _copy(REGION_SOURCE / "r.0.0.mdat", source / "nested" / "r.0.0.mdat")
    _copy(REGION_SOURCE / "r.0.0.mdat", source / "cached.mdat.bck")
    (source / "empty.mdat").touch()
    (source / "invalid.mdat").write_bytes(b"invalid")
    return source


@pytest.mark.parametrize("biomes", ("--biomes", "--no-biomes"))
@pytest.mark.parametrize("workers", (None, "0", "1", "2"))
def test_mapcache_smoke(biomes: str, workers: str | None, tmp_path: Path) -> None:
    source = _mapcache_sources(tmp_path)
    args = ["mapcache", str(source), "-O", str(tmp_path / "output"), biomes, "--verbose"]
    if workers is not None:
        args.extend(("-W", workers))
    _launch(args)


@pytest.mark.parametrize("kind", ("empty", "invalid-name", "broken-region", "file-source"))
def test_mapcache_invalid_input_smoke(kind: str, tmp_path: Path) -> None:
    source = tmp_path / "mapcache"
    if kind == "file-source":
        _copy(REGION_SOURCE / "r.0.0.mdat", source)
        _launch(["mapcache", str(source), "-O", str(tmp_path / "output"), "-W", "1"])
        return

    source.mkdir()

    if kind == "invalid-name":
        copy2(REGION_SOURCE / "r.0.0.mdat", source / "invalid.mdat")
    elif kind == "broken-region":
        (source / "r.0.0.mdat").write_bytes(b"broken")

    _launch(["mapcache", str(source), "-O", str(tmp_path / "output"), "-W", "1"])


def test_mapcache_existing_output_smoke(tmp_path: Path) -> None:
    source = _mapcache_sources(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    (output / "r.0.0.mca").write_bytes(b"existing")
    _launch(["mapcache", str(source), "-O", str(output), "-W", "2"])


def test_mapcache_default_output_smoke(tmp_path: Path) -> None:
    source = _mapcache_sources(tmp_path)
    _launch(["mapcache", str(source), "-W", "1"])


def test_implicit_convert_smoke(tmp_path: Path) -> None:
    source = tmp_path / "document.nbt"
    copy2(FORMATS / "document" / "source" / source.name, source)

    _launch([str(source)])


@pytest.mark.parametrize("kind", ("arms", "face", "body"))
def test_implicit_animation_smoke(kind: str, tmp_path: Path) -> None:
    model = tmp_path / MODEL_SOURCE.name
    copy2(MODEL_SOURCE, model)

    if kind == "body":
        animation = tmp_path / LIBRARY_SOURCE.name
        copy2(LIBRARY_SOURCE, animation)
        _launch([str(animation), str(model)])
        return

    animation = tmp_path / ("wpn_fp_animation.mcvd" if kind == "arms" else ANIMATION_SOURCE.name)
    copy2(ANIMATION_SOURCE, animation)
    _launch([str(animation), str(model)])


def test_implicit_arms_with_hands_smoke(tmp_path: Path) -> None:
    animation = _copy(ANIMATION_SOURCE, tmp_path / "wpn_fp_animation.mcvd")
    weapon = _copy(MODEL_SOURCE, tmp_path / "weapon.mcsb")
    hands = _copy(MODEL_SOURCE, tmp_path / "hands.mcsb")
    _launch([str(animation), str(weapon), str(hands)])


@pytest.mark.parametrize("kind", ("mcal-many-models", "mcvd-many-models", "mixed-models", "options"))
def test_implicit_convert_fallback_smoke(kind: str, tmp_path: Path) -> None:
    animation = _copy(ANIMATION_SOURCE, tmp_path / "animation.mcvd")
    weapon = _copy(MODEL_SOURCE, tmp_path / "weapon.mcsb")
    hands = _copy(MODEL_SOURCE, tmp_path / "hands.mcsb")

    match kind:
        case "mcal-many-models":
            library = _copy(LIBRARY_SOURCE, tmp_path / "library.mcal")
            _launch([str(library), str(weapon), str(hands)])
        case "mcvd-many-models":
            extra = _copy(MODEL_SOURCE, tmp_path / "extra.mcsb")
            renamed = _copy(animation, tmp_path / "wpn_fp_animation.mcvd")
            _launch([str(renamed), str(weapon), str(hands), str(extra)])
        case "mixed-models":
            texture = _copy(TEXTURE_SOURCE, tmp_path / "texture.ol")
            _launch([str(animation), str(weapon), str(texture)])
        case "options":
            _launch([str(animation), str(weapon), "-O", str(tmp_path / "output")])


def test_implicit_mapcache_smoke(tmp_path: Path) -> None:
    source = tmp_path / "map_cache"
    source.mkdir()
    copy2(REGION_SOURCE / "r.0.0.mdat", source / "r.0.0.mdat")

    _launch([str(source)])


@pytest.mark.parametrize(
    "args",
    [
        ["convert"],
        ["convert", str(DOCUMENT_SOURCE), "-I", "unknown"],
        ["convert", str(DOCUMENT_SOURCE), "--layout", "unknown"],
        ["animate"],
        ["animate", "arms"],
        ["mapcache"],
    ],
)
def test_cli_validation_smoke(args: list[str]) -> None:
    _launch(args)
