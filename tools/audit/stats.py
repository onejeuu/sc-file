import csv
import os
from collections import Counter
from pathlib import Path
from typing import Any, TextIO

from scfile.core import BaseContent, ImageContent, ModelContent, TextureContent
from scfile.formats.ol.enums import TextureKind
from scfile.structures.models import Flag
from scfile.structures.textures import CubemapTexture, DefaultTexture
from tools.audit.schemas import Animation, Bone, Image, Mesh, Model, Record, Texture
from tools.audit.types import Asset


_TABLES = {
    Model: "models.csv",
    Mesh: "meshes.csv",
    Bone: "bones.csv",
    Animation: "animations.csv",
    Texture: "textures.csv",
    Image: "images.csv",
}


def records(asset: Asset, content: BaseContent, root: Path) -> list[Record]:
    path = os.path.relpath(asset.path, root).replace("\\", "/")

    match content:
        case ModelContent():
            return _model(path, content, os.path.getsize(asset.path))

        case TextureContent():
            return _texture(path, content, os.path.getsize(asset.path))

        case ImageContent():
            return [Image(path=path, filesize=len(content.image))]

        case _:
            return []


def _model(path: str, content: ModelContent, filesize: int) -> list[Record]:
    meshes = [
        Mesh(
            path=path,
            idx=index,
            name=mesh.name,
            material=mesh.material,
            vertices=len(mesh.vertices),
            polygons=len(mesh.polygons),
            quads=mesh.quads,
            max_influences=mesh.max_influences,
        )
        for index, mesh in enumerate(content.scene.meshes)
    ]
    bones = [
        Bone(
            path=path,
            idx=bone.id,
            name=bone.name,
            parent_idx=bone.parent_id,
        )
        for bone in content.scene.skeleton.bones
    ]
    animations = [
        Animation(
            path=path,
            idx=index,
            name=clip.name,
            frames=clip.frames,
            rate=clip.rate,
        )
        for index, clip in enumerate(content.scene.animation.clips)
    ]
    scale = content.scene.scale
    model = Model(
        path=path,
        filesize=filesize,
        version=content.version,
        meshes=len(meshes),
        vertices=sum(mesh.vertices for mesh in meshes),
        polygons=sum(mesh.polygons for mesh in meshes),
        bones=len(bones),
        clips=len(animations),
        frames=sum(animation.frames for animation in animations),
        skeleton=bool(content.flags.get(Flag.SKELETON)),
        uv=bool(content.flags.get(Flag.UV)),
        uv2=bool(content.flags.get(Flag.UV2)),
        normals=bool(content.flags.get(Flag.NORMALS)),
        tangents=bool(content.flags.get(Flag.TANGENTS)),
        colors=bool(content.flags.get(Flag.COLORS)),
        scale=scale.position,
        scale_uv=scale.uv,
        scale_uv2=scale.uv2,
        scale_filtering=scale.filtering,
    )

    return [model, *meshes, *bones, *animations]


def _texture(path: str, content: TextureContent, filesize: int) -> list[Record]:
    match content.texture:
        case DefaultTexture() as texture:
            kind = TextureKind.DEFAULT.name
            faces = 1
            uncompressed_size = sum(texture.uncompressed)
            compressed_size = sum(texture.compressed)

        case CubemapTexture() as texture:
            kind = TextureKind.CUBEMAP.name
            faces = len(texture.faces)
            uncompressed_size = sum(map(sum, texture.uncompressed))
            compressed_size = sum(map(sum, texture.compressed))

        case _:
            return []

    return [
        Texture(
            path=path,
            filesize=filesize,
            scformat=content.format.decode(errors="replace"),
            fourcc=content.fourcc.decode(errors="replace"),
            width=content.width,
            height=content.height,
            kind=kind,
            mipmaps=content.mipmap_count,
            faces=faces,
            uncompressed_size=uncompressed_size,
            compressed_size=compressed_size,
            texture_id=content.texture_id.decode(errors="replace"),
        )
    ]


class Writer:
    def __init__(self, path: Path):
        self.path = path
        self._files: list[TextIO] = []
        self._writers: dict[type, Any] = {}

    def __enter__(self):
        self.path.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, *args):
        for file in self._files:
            file.close()

    def write(self, records: list[Record]) -> None:
        for record in records:
            table = type(record)
            writer = self._writers.get(table)

            if writer is None:
                file = (self.path / _TABLES[table]).open("w", newline="", encoding="utf-8")
                writer = csv.writer(file)
                writer.writerow(record._fields)
                self._files.append(file)
                self._writers[table] = writer

            writer.writerow(record)

    def formats(self, found: Counter, checked: Counter, failed: Counter) -> None:
        with (self.path / "formats.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("format", "files", "checked", "errors"))

            for format in sorted(found):
                writer.writerow((format, found[format], checked[format], failed[format]))
