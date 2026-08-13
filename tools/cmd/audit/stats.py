import csv
import os
from collections import Counter
from pathlib import Path
from typing import Any, TextIO

from scfile.formats.ol.enums import TextureKind
from scfile.structures import content as C
from scfile.structures.models import Feature
from scfile.structures.textures import CubemapTexture, DefaultTexture
from tools.cmd.audit.consts import FORMATS_CSV, TABLES
from tools.cmd.audit.schemas import Animation, Bone, Image, Mesh, Model, Record, Texture
from tools.cmd.audit.types import Asset


def records(
    asset: Asset,
    content: C.BaseContent,
    root: Path,
    animation: bool,
) -> list[Record]:
    path = os.path.relpath(asset.path, root).replace("\\", "/")

    match content:
        case C.ModelContent():
            return _model(path, content, os.path.getsize(asset.path), animation)

        case C.TextureContent():
            return _texture(path, content, os.path.getsize(asset.path))

        case C.ImageContent():
            return [Image(path=path, filesize=len(content.image))]

        case _:
            return []


def _model(
    path: str,
    content: C.ModelContent,
    filesize: int,
    animation: bool,
) -> list[Record]:
    meta = content.meta
    flags = meta.flags
    scene = content.scene
    scale = content.scene.scale

    meshes = [
        Mesh(
            path=path,
            idx=index,
            name=mesh.name,
            material=mesh.material,
            vertices=len(mesh.vertices),
            polygons=len(mesh.polygons),
            quads=mesh.polygon_quads,
            max_influences=mesh.max_influences if animation else "-",
        )
        for index, mesh in enumerate(scene.meshes)
    ]

    bones = [
        Bone(
            path=path,
            idx=bone.id,
            name=bone.name,
            parent_idx=bone.parent_id,
        )
        for bone in scene.skeleton.bones
    ]

    animations = [
        Animation(
            path=path,
            idx=index,
            name=clip.name,
            frames=clip.frames,
            rate=round(clip.rate, 3),
        )
        for index, clip in enumerate(scene.animation.clips)
    ]

    model = Model(
        path=path,
        filesize=filesize,
        version=meta.version,
        meshes=len(meshes),
        vertices=scene.total_vertices,
        polygons=scene.total_polygons,
        bones=len(bones) if animation else "-",
        clips=len(animations) if animation else "-",
        frames=sum(clip.frames for clip in animations) if animation else "-",
        skeleton=bool(flags.get(Feature.SKELETON)),
        uv=bool(flags.get(Feature.UV)),
        uv2=bool(flags.get(Feature.UV2)),
        normals=bool(flags.get(Feature.NORMALS)),
        tangents=bool(flags.get(Feature.TANGENTS)),
        colors=bool(flags.get(Feature.COLORS)),
        scale=scale.position,
        scale_uv=scale.uv,
        scale_uv2=scale.uv2,
    )

    if animation:
        return [model, *meshes, *bones, *animations]

    return [model, *meshes]


def _texture(
    path: str,
    content: C.TextureContent,
    filesize: int,
) -> list[Record]:
    match content.texture:
        case DefaultTexture() as texture:
            kind = TextureKind.DEFAULT.name
            faces = 1

        case CubemapTexture() as texture:
            kind = TextureKind.CUBEMAP.name
            faces = len(texture.faces)

        case _:
            return []

    return [
        Texture(
            path=path,
            filesize=filesize,
            fourcc=content.fourcc.decode(errors="replace"),
            width=content.width,
            height=content.height,
            kind=kind,
            mipmaps=content.mipmap_count,
            faces=faces,
            path_hash=content.path_hash.decode(errors="replace"),
        )
    ]


class Writer:
    def __init__(self, path: Path):
        self.path = path
        self._files: list[TextIO] = []
        self._writers: dict[type, Any] = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for file in self._files:
            file.close()

    def write(self, records: list[Record]) -> None:
        for record in records:
            table = type(record)
            writer = self._writers.get(table)

            if writer is None:
                file = (self.path / TABLES[table]).open("w", newline="", encoding="utf-8")
                writer = csv.writer(file)
                writer.writerow(record._fields)
                self._files.append(file)
                self._writers[table] = writer

            writer.writerow(record)

    def formats(self, found: Counter, checked: Counter, failed: Counter) -> None:
        with (self.path / FORMATS_CSV).open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("format", "files", "checked", "errors"))

            for format in sorted(found):
                writer.writerow((format, found[format], checked[format], failed[format]))
