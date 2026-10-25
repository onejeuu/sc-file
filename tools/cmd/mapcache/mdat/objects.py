from dataclasses import dataclass, field
from uuid import UUID

from scfile.content.base import DocumentValue
from scfile.exceptions import BinaryStructureError, SafetyLimitError
from scfile.io.nbt import NbtReader

from .binary import Reader
from .models import Note, ObjectItem, Objects, Placement, Slice, view


type Vector = tuple[float, float, float]


@dataclass(frozen=True)
class ObjectHeader:
    network_id: int
    flags: int
    flags2: int
    group: UUID | None
    material_patch: str | None
    client_csv: int
    client_cbv: int
    instance_serial: int


@dataclass(frozen=True)
class Settings:
    active: bool
    activation: int
    feature_flag: str | None
    render_collision_status: int | None
    collision_status: int
    render_model_selection: int
    custom_behaviour: str | None


@dataclass(frozen=True)
class Cable:
    shape_vertices: tuple[float, ...]
    shape_lines: tuple[int, ...]
    first_point: Vector
    second_point: Vector
    width: float
    segments_count: int
    uv_length_multiplier: float
    weight: float
    rigidity: float
    length: float
    cuboid: tuple[float, ...]


@dataclass(frozen=True)
class CurveNode:
    position: Vector
    direction: Vector
    up: Vector
    scale: tuple[float, float]
    roll: float
    points_per_segment: int


@dataclass(frozen=True)
class Curve:
    nodes: tuple[CurveNode, ...]
    shape_vertices: tuple[float, ...]
    shape_lines: tuple[int, ...]
    uv_length_multiplier: float
    cuboid: tuple[float, ...]


@dataclass(frozen=True)
class Behaviour:
    type: str
    raw: Slice
    data: DocumentValue | Cable | Curve


@dataclass(frozen=True)
class Appearance:
    brightness_override: int
    brightness_source: int
    diffuse_color: Vector
    mask_strength: float
    use_mask_color_as_tree_color: bool
    diffuse_color_mask: Vector
    culling_volume: UUID | None
    ignore_culling_volume: bool
    decoration_label: str | None
    no_cast_light_shadows: bool
    emission_color: Vector
    emission_map_opacity: float


@dataclass
class Instance:
    raw: Slice
    header: ObjectHeader | None = None
    placement: Placement | None = None
    settings: Settings | None = None
    behaviour: Behaviour | None = None
    appearance: Appearance | None = None
    consumed: int = 0
    notes: list[Note] = field(default_factory=list)

    @property
    def tail(self) -> Slice:
        return view(self.raw.data, self.consumed, len(self.raw.data) - self.consumed)


def read(data: bytes) -> Objects:
    raw = memoryview(data)
    result = Objects(raw)
    reader = Reader(raw)
    try:
        result.count = reader.varint()
        result.consumed = reader.offset
        for index in range(result.count):
            length_offset = reader.offset
            size = reader.varint()
            item = view(raw, reader.offset, size)
            reader.skip(size)
            result.items.append(ObjectItem(index, length_offset, item))
            result.consumed = reader.offset
    except EOFError as error:
        result.notes.append(Note("objects", reader.offset, str(error)))
    if result.tail.data and not result.notes:
        result.notes.append(Note("objects", result.tail.offset, "Bytes remain after declared items"))
    return result


def cable(reader: Reader) -> Cable:
    vertices = reader.floats(reader.number(">i"))
    lines = reader.numbers("i", reader.number(">i"))
    first, second = reader.vector(), reader.vector()
    width = reader.floats(1)[0]
    segments = reader.number(">i")
    uv, weight, rigidity, length = reader.floats(4)
    return Cable(vertices, lines, first, second, width, segments, uv, weight, rigidity, length, reader.floats(6))


def curve(reader: Reader) -> Curve:
    count = reader.number(">i")
    if count < 0 or count * 52 > len(reader.data) - reader.offset:
        raise EOFError(f"Curve node count {count} exceeds available bytes")
    nodes = []
    for _ in range(count):
        position, direction, up = reader.vector(), reader.vector(), reader.vector()
        sx, sy, roll = reader.floats(3)
        nodes.append(CurveNode(position, direction, up, (sx, sy), roll, reader.number(">i")))
    vertices = reader.floats(reader.number(">i"))
    lines = reader.numbers("i", reader.number(">i"))
    return Curve(tuple(nodes), vertices, lines, reader.floats(1)[0], reader.floats(6))


def instance(item: ObjectItem, behaviour: str | None = None) -> Instance:
    result = Instance(view(item.raw.data, 0, len(item.raw.data)))
    reader = Reader(item.raw.data)

    def stop(message: str) -> Instance:
        result.consumed = reader.offset
        result.notes.append(Note("objects", item.raw.offset + reader.offset, message))
        return result

    try:
        network = reader.number(">H")
        flags, flags2 = reader.unpack(">IB")
        if flags & ~0x3FBFF or flags2 & ~7:
            return stop("Unknown instance flag bits; optional field ordering is unavailable")
        group = reader.uuid() if flags & 0x80 else None
        patch = reader.utf() if flags & 0x8000 else None
        csv = reader.number(">i") if flags & 0x4000 else 16
        cbv = reader.number(">i") if flags & 0x2000 else -1
        result.header = ObjectHeader(network, flags, flags2, group, patch, csv, cbv, reader.number(">i"))
        start = reader.offset
        uuid = reader.uuid()
        columns = reader.vector(), reader.vector(), reader.vector()
        position = reader.vector()
        result.placement = Placement(
            uuid,
            columns,
            position,
            view(item.raw.data, start, 64),
            view(item.raw.data, reader.offset, len(item.raw.data) - reader.offset),
        )
        result.settings = Settings(
            bool(flags2 & 4),
            reader.number(">b"),
            reader.utf() if flags & 0x1000 else None,
            reader.number(">b") if flags & 0x800 else None,
            reader.number(">b"),
            reader.number(">B"),
            reader.utf() if flags & 0x200 else None,
        )
        start = reader.offset
        match behaviour:
            case "cable3d":
                data = cable(reader)
                name = "cable3d"
            case "curve":
                data = curve(reader)
                name = "curve"
            case _:
                if not reader.data[reader.offset :] or reader.data[reader.offset] != 10:
                    return stop("Behaviour serializer requires a matching definition; raw remainder retained")
                with NbtReader(reader.data[reader.offset :].tobytes(), errors="strict") as nbt:
                    data = nbt.document()
                    reader.skip(nbt.tell())
                name = "nbt"
        result.behaviour = Behaviour(name, view(item.raw.data, start, reader.offset - start), data)
        if flags2 & 1 or flags & 0x183:
            return stop("Runtime/editor/tag fields are not interpreted by this tool")
        brightness = reader.number(">i") if flags & 0x40 else -1
        source = reader.number(">b")
        diffuse = reader.vector() if flags & 0x20 else (1.0, 1.0, 1.0)
        strength = reader.floats(1)[0] if flags & 0x10 else 0.0
        tree = reader.number(">B") != 0
        mask = reader.vector() if flags & 8 else (1.0, 1.0, 1.0)
        volume = reader.uuid() if flags & 4 else None
        ignore = reader.number(">B") != 0
        label = reader.utf() if flags2 & 2 else None
        shadows = reader.number(">B") != 0
        emission = reader.vector() if flags & 0x10000 else (1.0, 1.0, 1.0)
        opacity = reader.floats(1)[0] if flags & 0x20000 else 0.0
        result.appearance = Appearance(
            brightness, source, diffuse, strength, tree, mask, volume, ignore, label, shadows, emission, opacity
        )
        result.consumed = reader.offset
        if result.tail.data:
            return stop("Bytes remain after the interpreted instance")
    except (EOFError, UnicodeError, BinaryStructureError, SafetyLimitError) as error:
        return stop(str(error))
    return result


def placement(item: ObjectItem) -> Placement | None:
    return instance(item).placement
