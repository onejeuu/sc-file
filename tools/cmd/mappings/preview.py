import io
import json
import math
import zipfile
from dataclasses import dataclass
from typing import Any, TypeAlias

from PIL import Image, ImageChops, ImageDraw, UnidentifiedImageError


Point3 = tuple[float, float, float]
Point2 = tuple[float, float]
Model: TypeAlias = dict[str, Any]
Transform: TypeAlias = dict[str, Any]
UV: TypeAlias = tuple[float, float, float, float] | list[tuple[float, float]]
FaceGeometry: TypeAlias = tuple[Point3, list[Point3], tuple[float, float, float, float]]


def tint_image(image: Image.Image, tint: str | None) -> Image.Image:
    if tint is None:
        return image
    color = tuple(int(tint[i : i + 2], 16) for i in (1, 3, 5))
    return ImageChops.multiply(image.convert("RGBA"), Image.new("RGBA", image.size, (*color, 255)))


def load_texture(
    jar: zipfile.ZipFile,
    name: str,
    crop: tuple[int, int, int, int] | list[int] | None = None,
    tint: str | None = None,
) -> Image.Image | None:
    try:
        image = Image.open(io.BytesIO(jar.read(f"assets/minecraft/textures/{name}.png"))).convert("RGBA")

    except (KeyError, OSError, UnidentifiedImageError):
        return None

    if crop:
        box = (crop[0], crop[1], crop[2], crop[3])
        image = image.crop(box)

    elif image.height > image.width:
        image = image.crop((0, 0, image.width, image.width))

    return tint_image(image, tint)


class ModelStore:
    def __init__(self, jar: zipfile.ZipFile) -> None:
        self.jar = jar
        self.files = set(jar.namelist())
        self.models: dict[str, Model] = {}
        self.textures: dict[str, Image.Image] = {}

    def load(self, path: str, parents: tuple[str, ...] = ()) -> Model:
        if path in self.models:
            return self.models[path]

        archive_path = f"assets/minecraft/models/{path}"
        if path in parents or archive_path not in self.files:
            return {"textures": {}, "elements": [], "display": {}}

        source = json.loads(self.jar.read(archive_path))
        parent_name = source.get("parent")
        parent = {}
        if isinstance(parent_name, str) and not parent_name.startswith("builtin/"):
            parent = self.load(f"{parent_name.removeprefix('minecraft:')}.json", (*parents, path))

        model: Model = {
            "textures": {**parent.get("textures", {}), **source.get("textures", {})},
            "elements": source.get("elements", parent.get("elements", [])),
            "display": {**parent.get("display", {}), **source.get("display", {})},
            "origin": source.get("origin", parent.get("origin")),
            "x": source.get("x", parent.get("x")),
            "y": source.get("y", parent.get("y")),
            "z": source.get("z", parent.get("z")),
            "texture_size": source.get("texture_size", parent.get("texture_size", (16, 16))),
        }
        self.models[path] = model
        return model

    def model(self, name: str) -> Model:
        return self.load(f"block/{name.removeprefix('minecraft:').removeprefix('block/')}.json")

    def item(self, name: str) -> Model:
        return self.load(f"item/{name.removeprefix('minecraft:').removeprefix('item/')}.json")

    def texture(self, name: str) -> Image.Image | None:
        if name not in self.textures:
            image = load_texture(self.jar, name)
            if image is None:
                return None
            self.textures[name] = image
        return self.textures[name].copy()


@dataclass
class RenderFace:
    depth: float
    polygon: list[Point2]
    texture: Image.Image
    source_points: list[Point2] | None


class ModelRenderer:
    DIRECTIONS = ("down", "up", "north", "south", "west", "east")
    CAMERAS = {"iso": (1 / math.sqrt(3),) * 3, "front": (0.0, 0.0, -1.0)}

    def __init__(self, jar: zipfile.ZipFile) -> None:
        self.store = ModelStore(jar)

    def rotate(self, point: Point3, axis: str, angle: float) -> Point3:
        x, y, z = point
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        if axis == "x":
            return x, y * c - z * s, y * s + z * c
        if axis == "y":
            return x * c + z * s, y, -x * s + z * c
        if axis == "z":
            return x * c - y * s, x * s + y * c, z
        raise ValueError(f"Unknown rotation axis: {axis}")

    def rotate_around(self, point: Point3, axis: str, angle: float, origin: Point3) -> Point3:
        relative: Point3 = (point[0] - origin[0], point[1] - origin[1], point[2] - origin[2])
        rotated = self.rotate(relative, axis, angle)
        return rotated[0] + origin[0], rotated[1] + origin[1], rotated[2] + origin[2]

    def rotate_model_point(self, point: Point3, model: dict, default_origin: Point3 = (8, 8, 8)) -> Point3:
        raw_origin = model.get("origin") or default_origin
        origin: Point3 = (float(raw_origin[0]), float(raw_origin[1]), float(raw_origin[2]))
        for axis in ("x", "y", "z"):
            if model.get(axis):
                point = self.rotate_around(point, axis, float(model[axis]), origin)
        return point

    def texture_name(self, reference: object, textures: dict[str, Any]) -> str | None:
        seen = set()
        while isinstance(reference, str) and reference.startswith("#"):
            key = reference[1:]
            if key in seen:
                return None
            seen.add(key)
            reference = textures.get(key)
        if not isinstance(reference, str):
            return None
        reference = reference.removeprefix("minecraft:")
        return reference.replace("block/", "blocks/", 1).replace("item/", "items/", 1)

    def project(self, point: Point3, view: str) -> Point2:
        x, y, z = point
        if view == "front":
            return x, -y
        if view != "iso":
            raise ValueError(f"Unknown preview view: {view}")
        return (x - z) * math.cos(math.pi / 6), (x + z) * 0.5 - y

    def face_geometry(self, direction: str, start: Point3, end: Point3) -> FaceGeometry:
        x1, y1, z1 = start
        x2, y2, z2 = end
        data: dict[str, FaceGeometry] = {
            "down": (
                (0, -1, 0),
                [(x1, y1, z2), (x2, y1, z2), (x2, y1, z1), (x1, y1, z1)],
                (x1, 16 - z2, x2, 16 - z1),
            ),
            "up": (
                (0, 1, 0),
                [(x1, y2, z1), (x2, y2, z1), (x2, y2, z2), (x1, y2, z2)],
                (x1, z1, x2, z2),
            ),
            "north": (
                (0, 0, -1),
                [(x1, y2, z1), (x2, y2, z1), (x2, y1, z1), (x1, y1, z1)],
                (x1, 16 - y2, x2, 16 - y1),
            ),
            "south": (
                (0, 0, 1),
                [(x2, y2, z2), (x1, y2, z2), (x1, y1, z2), (x2, y1, z2)],
                (16 - x2, 16 - y2, 16 - x1, 16 - y1),
            ),
            "west": (
                (-1, 0, 0),
                [(x1, y2, z1), (x1, y2, z2), (x1, y1, z2), (x1, y1, z1)],
                (z1, 16 - y2, z2, 16 - y1),
            ),
            "east": (
                (1, 0, 0),
                [(x2, y2, z2), (x2, y2, z1), (x2, y1, z1), (x2, y1, z2)],
                (16 - z2, 16 - y2, 16 - z1, 16 - y1),
            ),
        }
        return data[direction]

    def render(
        self,
        models: list[Model],
        tint: str | None,
        view: str = "iso",
        size: int = 72,
        transform: Transform | None = None,
    ) -> Image.Image | None:
        faces = [face for spec in models for face in self.render_model(spec, tint, view, transform)]
        return self.draw_faces(faces, view, size) if faces else None

    def render_model(
        self,
        spec: Model,
        tint: str | None,
        view: str,
        transform: Transform | None,
    ) -> list[RenderFace]:
        if "elements" in spec:
            model = spec
        else:
            model = self.store.model(spec["name"])
            model = {
                **model,
                **{key: spec[key] for key in ("origin", "x", "y", "z", "texture_size") if key in spec},
            }
        camera = self.CAMERAS[view]
        faces = []
        for element in model.get("elements", ()):
            raw_start = element.get("from", (0, 0, 0))
            raw_end = element.get("to", (16, 16, 16))
            start: Point3 = (float(raw_start[0]), float(raw_start[1]), float(raw_start[2]))
            end: Point3 = (float(raw_end[0]), float(raw_end[1]), float(raw_end[2]))

            for direction in self.DIRECTIONS:
                definition = element.get("faces", {}).get(direction)
                if not isinstance(definition, dict):
                    continue

                face = self.render_face(
                    model, element, definition, direction, start, end, camera, view, tint, transform
                )
                if face:
                    faces.append(face)

        return faces

    def render_face(
        self,
        model: Model,
        element: Model,
        definition: Model,
        direction: str,
        start: Point3,
        end: Point3,
        camera: Point3,
        view: str,
        tint: str | None,
        transform: Transform | None,
    ) -> RenderFace | None:
        normal, vertices, default_uv = self.face_geometry(direction, start, end)
        rotation = element.get("rotation")
        if rotation:
            raw_origin = rotation.get("origin", (8, 8, 8))
            origin: Point3 = (float(raw_origin[0]), float(raw_origin[1]), float(raw_origin[2]))
            vertices = [self.rotate_around(v, rotation["axis"], rotation.get("angle", 0), origin) for v in vertices]
            normal = self.rotate(normal, rotation["axis"], rotation.get("angle", 0))

        vertices = [self.rotate_model_point(v, model) for v in vertices]
        normal = self.rotate_model_point(normal, model, (0, 0, 0))
        if transform:
            vertices = [self.item_point(v, transform) for v in vertices]
            normal = self.item_normal(normal, transform)

        if sum(normal[i] * camera[i] for i in range(3)) <= 0:
            return None

        name = self.texture_name(definition.get("texture"), model.get("textures", {}))
        texture = self.store.texture(name) if name else None
        if texture is None:
            return None

        crop, source = self.crop_face(
            texture, definition.get("uv", default_uv), model.get("texture_size", (16, 16)), definition.get("rotation")
        )

        if tint:
            crop = tint_image(crop, tint)

        if transform:
            light = Image.new("RGBA", crop.size, (self.brightness(normal),) * 3 + (255,))
            crop = ImageChops.multiply(crop, light)

        projected = [self.project(v, view) for v in vertices]
        depth = sum(sum(v[i] * camera[i] for i in range(3)) for v in vertices) / 4
        return RenderFace(depth, projected, crop, source)

    def crop_face(
        self,
        texture: Image.Image,
        uv: UV,
        texture_size: tuple[int, int],
        rotation: int | None,
    ) -> tuple[Image.Image, list[Point2] | None]:
        if isinstance(uv, list) and uv and isinstance(uv[0], (list, tuple)):
            points = [
                (float(u) * texture.width / texture_size[0], float(v) * texture.height / texture_size[1]) for u, v in uv
            ]
            left, top = math.floor(min(x for x, _ in points)), math.floor(min(y for _, y in points))
            right, bottom = math.ceil(max(x for x, _ in points)), math.ceil(max(y for _, y in points))
            return texture.crop((left, top, right, bottom)), [(x - left, y - top) for x, y in points]

        u1, v1, u2, v2 = uv
        crop = texture.crop(
            (
                round(min(u1, u2) * texture.width / 16),
                round(min(v1, v2) * texture.height / 16),
                round(max(u1, u2) * texture.width / 16),
                round(max(v1, v2) * texture.height / 16),
            )
        )

        if u2 < u1:
            crop = crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        if v2 < v1:
            crop = crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        if rotation:
            crop = crop.rotate(-rotation, expand=False)

        return crop, None

    def item_point(self, point: Point3, transform: Transform) -> Point3:
        point = (point[0] - 8, point[1] - 8, point[2] - 8)
        for axis, angle in zip(("x", "y", "z"), transform.get("rotation", (0, 0, 0))):
            point = self.rotate(point, axis, angle)

        scale, translation = transform.get("scale", (1, 1, 1)), transform.get("translation", (0, 0, 0))
        return (
            point[0] * scale[0] + translation[0],
            point[1] * scale[1] + translation[1],
            point[2] * scale[2] + translation[2],
        )

    def item_normal(self, normal: Point3, transform: Transform) -> Point3:
        for axis, angle in zip(("x", "y", "z"), transform.get("rotation", (0, 0, 0))):
            normal = self.rotate(normal, axis, angle)
        return normal

    def brightness(self, normal: Point3) -> int:
        normal = (normal[0], -normal[1], normal[2])
        value = 0.4
        for light in ((0.2, 1.0, -0.7), (-0.2, 1.0, 0.7)):
            light = self.rotate(self.rotate(light, "x", 165), "y", -30)
            length = math.sqrt(sum(v * v for v in light))
            value += 0.6 * max(sum(normal[i] * light[i] for i in range(3)) / length, 0)

        return round(min(value, 1.0) * 255)

    def affine(
        self,
        destination: list[Point2],
        source: list[Point2],
        left: int,
        top: int,
    ) -> tuple[float, ...] | None:
        (x0, y0), (x1, y1), (x2, y2) = destination[:3]
        (u0, v0), (u1, v1), (u2, v2) = source[:3]
        x0, x1, x2, y0, y1, y2 = x0 - left, x1 - left, x2 - left, y0 - top, y1 - top, y2 - top
        dx1, dy1, dx2, dy2 = x1 - x0, y1 - y0, x2 - x0, y2 - y0

        determinant = dx1 * dy2 - dx2 * dy1
        if abs(determinant) < 1e-8:
            return None

        du1, dv1, du2, dv2 = u1 - u0, v1 - v0, u2 - u0, v2 - v0
        a, b = (du1 * dy2 - du2 * dy1) / determinant, (dx1 * du2 - dx2 * du1) / determinant
        d, e = (dv1 * dy2 - dv2 * dy1) / determinant, (dx1 * dv2 - dx2 * dv1) / determinant

        return a, b, u0 - a * x0 - b * y0, d, e, v0 - d * x0 - e * y0

    def draw_faces(self, faces: list[RenderFace], view: str, size: int) -> Image.Image | None:
        points = [p for face in faces for p in face.polygon]
        min_x, max_x = min(x for x, _ in points), max(x for x, _ in points)
        min_y, max_y = min(y for _, y in points), max(y for _, y in points)
        span = max(max_x - min_x, max_y - min_y)

        if span <= 0:
            return None

        scale = min((size - 12) / span, 4.0 if view == "front" else 3.0)
        offset_x = (size - (max_x - min_x) * scale) / 2 - min_x * scale
        offset_y = (size - (max_y - min_y) * scale) / 2 - min_y * scale
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        for face in sorted(faces, key=lambda f: f.depth):
            destination = [(x * scale + offset_x, y * scale + offset_y) for x, y in face.polygon]
            left, top = (
                max(0, math.floor(min(x for x, _ in destination))),
                max(0, math.floor(min(y for _, y in destination))),
            )
            right, bottom = (
                min(size, math.ceil(max(x for x, _ in destination))),
                min(size, math.ceil(max(y for _, y in destination))),
            )

            if right <= left or bottom <= top:
                continue

            source = face.source_points or [(0, 0), (face.texture.width, 0), (face.texture.width, face.texture.height)]
            affine = self.affine(destination, source, left, top)
            if affine is None:
                continue

            warped = face.texture.transform(
                (right - left, bottom - top), Image.Transform.AFFINE, affine, resample=Image.Resampling.NEAREST
            )
            mask = Image.new("L", warped.size, 0)
            ImageDraw.Draw(mask).polygon([(x - left, y - top) for x, y in destination], fill=255)
            warped.putalpha(ImageChops.multiply(warped.getchannel("A"), mask))
            canvas.alpha_composite(warped, (left, top))

        return canvas

    def render_item(
        self,
        name: str,
        tint: str | None,
        size: int = 72,
        model_override: Model | None = None,
    ) -> Image.Image | None:
        model = self.store.item(name)
        if model_override:
            model = {**model, **model_override}

        return (
            self.render([model], tint, "front", size, model.get("display", {}).get("gui", {}))
            if model.get("elements")
            else None
        )


def render_banner(jar: zipfile.ZipFile, texture_name: str, size: int = 72) -> Image.Image | None:
    texture = load_texture(jar, texture_name)
    if texture is None:
        return None

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    image.alpha_composite(texture.crop((0, 0, 40, 40)).resize((42, 48), Image.Resampling.NEAREST), (15, 10))
    draw = ImageDraw.Draw(image)
    draw.rectangle((13, 8, 58, 59), outline=(35, 29, 22, 255), width=2)
    draw.rectangle((35, 4, 37, 64), fill=(111, 77, 44, 255))

    return image


def render_preview(
    jar: zipfile.ZipFile,
    renderer: ModelRenderer,
    spec: Model,
    tint: str | None,
) -> Image.Image | None:
    if "texture" in spec:
        return load_texture(jar, spec["texture"], spec.get("crop"), tint)
    if "item" in spec:
        return renderer.render_item(spec["item"], tint, model_override=spec.get("model"))
    if "banner" in spec:
        return render_banner(jar, spec["banner"])
    if "models" in spec:
        return renderer.render(spec["models"], tint, spec.get("view", "iso"), transform=spec.get("transform"))
    raise ValueError(f"Unknown preview specification: {spec}")
