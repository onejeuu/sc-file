import gzip
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageChops, UnidentifiedImageError
from rich import print

from scfile import formats
from tools.paths import ROOT


ASSETS = ROOT / "assets" / "mappings"
REPORTS = ROOT / "reports" / "mappings"
STALCRAFT_CATALOG = ASSETS / "stalcraft.json.gz"
MINECRAFT_CATALOG = ASSETS / "minecraft.json.gz"

GRASS_TINT = (0x91, 0xBD, 0x59)
FOLIAGE_TINT = (0x77, 0xAB, 0x2F)
WATER_TINT = (0x3F, 0x76, 0xE4)


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


def extract_stalcraft(source: Path) -> None:
    with gzip.open(STALCRAFT_CATALOG, "rt", encoding="utf-8") as file:
        catalog = json.load(file)
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
    print(
        f"[bold cyan]Stalcraft[/] {len(index)} blocks, "
        f"{decoded} previews, {len(missing)} missing DDS."
    )


def preview_tint(name: str) -> tuple[int, int, int] | None:
    if name in {
        "grass_top",
        "grass_side_overlay",
        "tallgrass",
        "fern",
        "double_plant_grass_top",
        "double_plant_grass_bottom",
        "double_plant_fern_top",
        "double_plant_fern_bottom",
    }:
        return GRASS_TINT
    if name.startswith("leaves_"):
        if name == "leaves_spruce":
            return (0x61, 0x99, 0x61)
        if name == "leaves_birch":
            return (0x80, 0xA7, 0x55)
        return FOLIAGE_TINT
    if name in {"vine", "waterlily"}:
        return FOLIAGE_TINT
    if name in {"water_still", "water_flow"}:
        return WATER_TINT
    return None


def extract_minecraft(source: Path) -> None:
    with gzip.open(MINECRAFT_CATALOG, "rt", encoding="utf-8") as file:
        catalog = json.load(file)
    output = REPORTS / "minecraft"
    textures = output / "textures"
    textures.mkdir(parents=True, exist_ok=True)

    prefix = "assets/minecraft/textures/blocks/"
    outputs = []
    placeholders = {}
    unmatched = []
    seen = set()
    written = {}

    with zipfile.ZipFile(source) as jar:
        names = {name[len(prefix) : -4] for name in jar.namelist() if name.startswith(prefix) and name.endswith(".png")}
        if not names:
            raise ValueError("Minecraft JAR has no assets/minecraft/textures/blocks/*.png textures.")

        for record in catalog:
            texture = next((name for name in record["texture_candidates"] if name in names), None)
            block_id = record["id"]
            if texture is None:
                unmatched.append(f"{block_id}:{record['meta']}")
                placeholders.setdefault(
                    block_id,
                    {
                        "id": block_id,
                        "meta": record["meta"],
                        "name": record["name"],
                        "display": record["display"],
                        "texture": None,
                        "textureName": None,
                    },
                )
                continue

            if (block_id, texture) in seen:
                continue
            seen.add((block_id, texture))

            if texture not in written:
                raw = jar.read(prefix + texture + ".png")
                with Image.open(io.BytesIO(raw)) as image:
                    image = image.convert("RGBA")
                    if image.height > image.width:
                        image = image.crop((0, 0, image.width, image.width))
                    tint = preview_tint(texture)
                    if tint is not None:
                        image = ImageChops.multiply(image, Image.new("RGBA", image.size, (*tint, 255)))
                    relative = f"textures/{hashlib.sha1(texture.encode()).hexdigest()[:16]}.png"
                    image.save(output / relative, optimize=True)
                written[texture] = relative

            outputs.append(
                {
                    "id": block_id,
                    "meta": record["meta"],
                    "name": record["name"],
                    "display": record["display"],
                    "texture": written[texture],
                    "textureName": texture,
                }
            )

    available_ids = {record["id"] for record in outputs}
    outputs.extend(record for block_id, record in placeholders.items() if block_id not in available_ids)
    outputs.sort(key=lambda record: (record["id"], record["meta"]))

    save_json(output / "index.json", outputs)
    save_json(
        output / "report.json",
        {
            "textures_in_jar": len(names),
            "materials": len(outputs),
            "blocks": len({record["id"] for record in outputs}),
            "blocks_without_preview": sorted(record["id"] for record in outputs if record["texture"] is None),
            "unmatched_materials": len(unmatched),
        },
    )
    if not written:
        raise ValueError("No Minecraft catalog textures were found in the configured JAR.")

    print(
        f"[bold magenta]Minecraft[/] {len(outputs)} materials, "
        f"{len({record['id'] for record in outputs})} IDs, {len(written)} textures."
    )
