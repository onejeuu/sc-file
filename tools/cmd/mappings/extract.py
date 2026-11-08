import gzip
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from PIL import Image, UnidentifiedImageError
from rich import print

from scfile import formats
from tools.paths import ROOT

from .preview import ModelRenderer, ResourcePack, load_texture, render_preview


ASSETS = ROOT / "assets" / "mappings"
REPORTS = ROOT / "reports" / "mappings"
STALCRAFT_CATALOG = ASSETS / "stalcraft.json.gz"
MINECRAFT_CATALOG = ASSETS / "minecraft.json.gz"


class MinecraftStats(TypedDict):
    written: dict[tuple, str]
    preview_written: dict[str, str | None]
    unmatched: list[str]
    fallbacks: list[dict]


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def path_key(name: str) -> str:
    name = name.replace("\\", "/").strip().strip("\x00").lower().replace(":", "/")
    return re.sub(r"/+", "/", name).lstrip("/").removesuffix(".dds")


def aliases(name: str) -> tuple[str, ...]:
    key = path_key(name)
    parts = key.split("/")
    return tuple(dict.fromkeys((key, *("/".join(parts[index:]) for index in range(1, len(parts))), parts[-1])))


def read_catalog(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, list):
        raise ValueError(f"Mapping catalog must contain an array: {path}")
    return value


def extract_stalcraft(source: Path) -> None:
    catalog = read_catalog(STALCRAFT_CATALOG)
    output = REPORTS / "stalcraft"
    textures = output / "textures"
    textures.mkdir(parents=True, exist_ok=True)

    wanted = {alias for block in catalog for view in block["views"] for alias in aliases(view["dds"])}
    entries: dict[str, tuple[str, bytes]] = {}
    basename_hits: dict[str, list[tuple[str, bytes]]] = defaultdict(list)

    with formats.TexarrDecoder(source) as decoder:
        for name, data in decoder.decode().entries:
            key = path_key(name)
            entry = (name, data)
            for alias in aliases(name):
                if alias in wanted:
                    entries.setdefault(alias, entry)

            basename_hits[key.rsplit("/", 1)[-1]].append(entry)

    def resolve(name: str) -> tuple[str, bytes] | None:
        key = path_key(name)
        hit = entries.get(key)

        if hit is not None:
            return hit

        for alias in aliases(name):
            hit = entries.get(alias)
            if hit is not None:
                return hit

        matches = basename_hits.get(key.rsplit("/", 1)[-1], [])
        return matches[0] if len(matches) == 1 else None

    decoded = 0
    written = {}
    missing = set()
    decode_errors = []
    index = []

    for block in catalog:
        views = []
        for view in block["views"]:
            hit = resolve(view["dds"])
            preview = None

            if hit is None:
                missing.add(view["dds"])
            else:
                name, data = hit
                key = path_key(name)
                preview = written.get(key)
                if preview is None:
                    preview = f"textures/{hashlib.sha1(key.encode()).hexdigest()[:18]}.png"
                    try:
                        with Image.open(io.BytesIO(data)) as image:
                            image.seek(0)
                            image.convert("RGBA").save(output / preview, optimize=True)
                        written[key] = preview
                        decoded += 1

                    except (UnidentifiedImageError, OSError, ValueError) as error:
                        preview = None
                        decode_errors.append({"dds": name, "error": str(error)})

            views.append({**view, "primary": preview})

        index.append({key: value for key, value in block.items() if key != "views"} | {"views": views})

    save_json(output / "index.json", index)
    save_json(
        output / "report.json",
        {
            "blocks": len(index),
            "views": sum(len(block["views"]) for block in index),
            "decoded_textures": decoded,
            "missing_textures": sorted(missing),
            "decode_errors": decode_errors,
            "blocks_without_preview": [
                block["id"] for block in index if not any(view["primary"] for view in block["views"])
            ],
        },
    )

    if not decoded:
        raise ValueError("No Stalcraft textures were decoded from the configured TEXARR.")

    print(f"[bold yellow]Stalcraft[/] {len(index)} blocks, {decoded} previews, {len(missing)} missing DDS.")


def extract_minecraft(source: Path, resourcepack: Path | None = None) -> None:
    catalog = read_catalog(MINECRAFT_CATALOG)

    output = REPORTS / "minecraft"
    textures = output / "textures"
    previews = output / "previews"
    for directory in (textures, previews):
        directory.mkdir(parents=True, exist_ok=True)
        for path in directory.glob("*.png"):
            path.unlink()

    texture_root = "assets/minecraft/textures/"

    with zipfile.ZipFile(source) as jar:
        pack = ResourcePack(resourcepack) if resourcepack is not None else None
        try:
            names = {
                name[len(texture_root) : -4]
                for name in jar.namelist()
                if name.startswith(texture_root) and name.endswith(".png")
            }
            if pack is not None:
                names.update(pack.names(texture_root))

            if not names:
                raise ValueError("Minecraft JAR has no assets/minecraft/textures/*.png textures.")

            renderer = ModelRenderer(jar, pack)
            outputs, stats = build_minecraft_outputs(catalog, jar, pack, renderer, names, output)
        finally:
            if pack is not None:
                pack.close()

    outputs.sort(key=lambda record: (record["id"], record["meta"]))
    save_json(output / "index.json", outputs)
    save_json(
        output / "report.json",
        {
            "textures_in_jar": len(names),
            "materials": len(outputs),
            "blocks": len({record["id"] for record in outputs}),
            "blocks_without_preview": sorted(record["id"] for record in outputs if not record["texture"]),
            "blocks_without_catalog_preview": sorted(
                record["id"] for record in outputs if not record["catalogPreview"]
            ),
            "unmatched_textures": stats["unmatched"],
            "catalog_previews": len(stats["preview_written"]),
            "preview_fallbacks": stats["fallbacks"],
        },
    )

    if not stats["written"] and not stats["preview_written"]:
        raise ValueError("No Minecraft catalog textures were found in the configured JAR.")

    print(
        f"[bold green]Minecraft[/] {len(outputs)} materials, "
        f"{len({record['id'] for record in outputs})} IDs, {len(stats['written'])} textures, "
        f"{len(stats['preview_written'])} catalog previews."
    )


def build_minecraft_outputs(
    catalog: list[dict],
    jar: zipfile.ZipFile,
    resourcepack: ResourcePack | None,
    renderer: ModelRenderer,
    names: set[str],
    output: Path,
) -> tuple[list[dict], MinecraftStats]:
    outputs = []
    unmatched = []
    fallbacks = []
    written = {}
    preview_written = {}
    seen = set()

    for record in catalog:
        texture_name = record["texture"]
        block_id = record["id"]
        crop = tuple(record["textureCrop"]) if record.get("textureCrop") else None
        tint = record.get("tint")
        from_preview = record.get("mappingTextureFromPreview", False)

        key = (block_id, texture_name, crop, tint, from_preview)
        if key in seen:
            continue

        seen.add(key)

        if texture_name not in names:
            unmatched.append(f"{block_id}:{record['meta']}:{texture_name}")

        flat_preview = (
            write_flat_texture(resourcepack or jar, output, texture_name, crop, tint, written)
            if not from_preview
            else None
        )
        if flat_preview is None and resourcepack is not None and not from_preview:
            flat_preview = write_flat_texture(jar, output, texture_name, crop, tint, written)
        catalog_preview = write_catalog_preview(
            jar, renderer, output, record.get("preview"), tint, flat_preview, preview_written, fallbacks, record
        )
        if from_preview:
            flat_preview = catalog_preview

        outputs.append(
            {
                "id": block_id,
                "meta": record["meta"],
                "name": record["name"],
                "display": record["display"],
                "texture": flat_preview,
                "textureName": texture_name,
                "catalogPreview": catalog_preview,
            }
        )

    return outputs, {
        "written": written,
        "preview_written": preview_written,
        "unmatched": unmatched,
        "fallbacks": fallbacks,
    }


def write_flat_texture(
    source: zipfile.ZipFile | ResourcePack, output: Path, name: str, crop, tint, written: dict[tuple, str]
) -> str | None:
    key = (name, crop, tint)
    if key in written:
        return written[key]

    image = load_texture(source, name, crop, tint)
    if image is None:
        return None

    relative = f"textures/{hashlib.sha1(repr(key).encode()).hexdigest()[:16]}.png"
    image.save(output / relative, optimize=True)
    written[key] = relative
    return relative


def write_catalog_preview(
    jar: zipfile.ZipFile,
    renderer: ModelRenderer,
    output: Path,
    spec,
    tint,
    fallback: str | None,
    written: dict[str, str | None],
    fallbacks: list[dict],
    record: dict,
) -> str | None:
    if not spec:
        return fallback
    key = json.dumps([spec, tint], sort_keys=True, separators=(",", ":"))
    if key in written:
        return written[key]
    image = render_preview(jar, renderer, spec, tint)
    if image is None:
        fallbacks.append({"id": record["id"], "meta": record["meta"], "preview": spec})
        written[key] = fallback
        return fallback
    relative = f"previews/{hashlib.sha1(key.encode()).hexdigest()[:16]}.png"
    image.save(output / relative, optimize=True)
    written[key] = relative
    return relative
