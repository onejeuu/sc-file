from dataclasses import dataclass

from .mdat.models import XYZ, Chunk, Record, State
from .mdat.terrain import Terrain
from .metadata import BlockDefinition, Catalog


SIDES = ("down", "up", "north", "south", "west", "east", "main")


@dataclass(frozen=True)
class Face:
    slot: int
    side: str
    cover: State
    definition: BlockDefinition | None
    color_rgb565: int | None
    color: tuple[float, float, float] | None
    color_exponent: int
    overlay: int
    rotation_quarters: int | None
    ctm_data: int | None
    packed: bool


@dataclass(frozen=True)
class Box:
    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]


@dataclass(frozen=True)
class Grid:
    mask: str
    cells: tuple[XYZ, ...]


@dataclass(frozen=True)
class Collapsible:
    direction: int
    corner_steps: tuple[int, int, int, int]
    clamped_steps: tuple[int, int, int, int]


@dataclass(frozen=True)
class Carpenter:
    faces: tuple[Face, ...]
    shape: Box | Grid | Collapsible | None


def state_at(record: Record, chunk: Chunk, terrain: Terrain) -> State | None:
    if chunk.coordinates is None:
        return None
    cx, cz = chunk.coordinates
    x, y, z = record.header.position
    local = x - cx * 16, y, z - cz * 16
    if not (0 <= local[0] < 16 and 0 <= y < 256 and 0 <= local[2] < 16):
        return None
    return terrain.block(local, chunk).state


def interpret(record: Record, state: State | None, catalog: Catalog | None = None) -> Carpenter:
    payload = record.payload
    covers = payload.covers if payload.flags & 8 else (0,) * 6 + payload.covers
    colors = payload.color_short or (-1,) * 7
    overlays = payload.overlay or (0,) * 7
    ctm = payload.ctm_data or (0,) * 6
    rot = payload.rot or 0
    exponent = payload.color_exponent or 0
    packed = payload.packcovers or 0
    faces = []
    for slot, side in enumerate(SIDES):
        cover = State(covers[slot] & 0xFFFF)
        color = colors[slot] & 0xFFFF if colors[slot] != -1 else None
        rgb = ((color >> 11) / 31, ((color >> 5) & 63) / 63, (color & 31) / 31) if color is not None else None
        rotation = (((rot >> (slot * 2)) & 3) + ((ctm[slot] >> 6) & 3)) % 4 if slot < 6 else None
        faces.append(
            Face(
                slot,
                side,
                cover,
                catalog.block(cover) if catalog else None,
                color,
                rgb,
                (exponent >> (slot * 2)) & 3,
                overlays[slot],
                rotation,
                ctm[slot] & 255 if slot < 6 else None,
                bool(packed & (1 << slot)),
            )
        )
    shape = None
    if record.header.type == 1:
        bits = ((payload.data_ext or 0) & 0xFFFFFFFF) << 32 | payload.data & 0xFFFFFFFF
        cells = tuple(
            (x, y, z) for y in range(4) for z in range(4) for x in range(4) if bits & (1 << (y * 16 + z * 4 + x))
        )
        shape = Grid(f"0x{bits:016x}", cells)
    elif state is not None and state.block_id == 2405 and 0 <= payload.data <= 6:
        minimum = [0.0, 0.0, 0.0]
        maximum = [1.0, 1.0, 1.0]
        if payload.data:
            axis = (payload.data - 1) // 2
            if payload.data % 2:
                maximum[axis] = 0.5
            else:
                minimum[axis] = 0.5
        shape = Box((minimum[0], minimum[1], minimum[2]), (maximum[0], maximum[1], maximum[2]))
    elif state is not None and state.block_id == 2486:
        steps = tuple((payload.data >> shift) & 31 for shift in (18, 13, 8, 3))
        shape = Collapsible(
            payload.data & 7,
            (steps[0], steps[1], steps[2], steps[3]),
            (min(steps[0], 16), min(steps[1], 16), min(steps[2], 16), min(steps[3], 16)),
        )
    return Carpenter(tuple(faces), shape)
