from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .models import XYZ, Chunk, Header, Note, Slice, view
from .reader import decompress


@dataclass(frozen=True)
class State:
    value: int

    @property
    def block_id(self) -> int:
        return self.value & 0xFFF

    @property
    def metadata(self) -> int:
        return self.value >> 12

    @property
    def addition(self) -> int:
        return (self.value >> 8) & 15


@dataclass(frozen=True)
class Sample:
    plane: str
    offset: int | None
    byte: int | None
    value: int | None
    nibble: Literal["low", "high"] | None = None


@dataclass(frozen=True)
class Block:
    local: XYZ
    world: XYZ | None
    section: int
    index: int
    status: Literal["stored", "absent", "unavailable"]
    state: State | None
    samples: tuple[Sample, ...]


def nibble(raw: memoryview, index: int) -> int:
    return (raw[index // 2] >> (4 * (index & 1))) & 15


def nibbles(raw: memoryview) -> NDArray[np.uint16]:
    packed = np.frombuffer(raw, dtype=np.uint8)
    result = np.empty(len(packed) * 2, dtype=np.uint16)
    result[::2] = packed & 15
    result[1::2] = packed >> 4
    return result


@dataclass(frozen=True)
class Section:
    y: int
    blocks: Slice
    metadata: Slice
    lighting: tuple[Slice, Slice, Slice]
    additions: Slice | None

    def states(self) -> NDArray[np.uint16] | None:
        planes = (self.blocks, self.metadata)
        if not all(plane.complete for plane in planes) or (self.additions is not None and not self.additions.complete):
            return None
        result = np.frombuffer(self.blocks.data, dtype=np.uint8).astype(np.uint16)
        result |= nibbles(self.metadata.data) << 12
        if self.additions is not None:
            result |= nibbles(self.additions.data) << 8
        return result.reshape(16, 16, 16)


class Terrain:
    def __init__(self, header: Header, data: bytes):
        self.header = header
        self.raw = memoryview(data)
        ys = tuple(y for y in range(16) if header.section_mask & (1 << y))
        adds = tuple(y for y in range(16) if header.add_mask & (1 << y))
        count = len(ys)
        self.blocks = view(self.raw, 0, count * 4096)
        self.metadata = view(self.raw, self.blocks.end, count * 2048)
        light0 = view(self.raw, self.metadata.end, count * 2048)
        light1 = view(self.raw, light0.end, count * 2048)
        light2 = view(self.raw, light1.end, count * 2048)
        self.lighting = light0, light1, light2
        self.additions = view(self.raw, light2.end, len(adds) * 2048)
        self.biomes = view(self.raw, self.additions.end, 256)
        self.records = view(self.raw, self.biomes.end, max(0, len(self.raw) - self.biomes.end))
        self.sections = tuple(
            Section(
                y,
                view(self.raw, self.blocks.offset + index * 4096, 4096),
                view(self.raw, self.metadata.offset + index * 2048, 2048),
                (
                    view(self.raw, light0.offset + index * 2048, 2048),
                    view(self.raw, light1.offset + index * 2048, 2048),
                    view(self.raw, light2.offset + index * 2048, 2048),
                ),
                view(self.raw, self.additions.offset + adds.index(y) * 2048, 2048) if y in adds else None,
            )
            for index, y in enumerate(ys)
        )
        self.notes: list[Note] = []
        if self.biomes.end > len(self.raw):
            self.notes.append(Note("terrain", len(self.raw), "Incomplete terrain planes"))

    @classmethod
    def from_chunk(cls, chunk: Chunk) -> "Terrain | None":
        if chunk.header is None or chunk.terrain is None:
            return None
        data = decompress(chunk.terrain, chunk.notes)
        return cls(chunk.header, data) if data is not None else None

    def block(self, position: XYZ, chunk: Chunk) -> Block:
        x, y, z = position
        index = (y & 15) * 256 + z * 16 + x
        world = None

        if chunk.coordinates is not None:
            cx, cz = chunk.coordinates
            world = cx * 16 + x, y, cz * 16 + z

        section = next((section for section in self.sections if section.y == y // 16), None)

        if section is None:
            return Block(position, world, y // 16, index, "absent", None, ())

        samples: list[Sample] = []
        for name, plane in (
            ("blocks", section.blocks),
            ("metadata", section.metadata),
            ("additions", section.additions),
            ("lighting_0", section.lighting[0]),
            ("lighting_1", section.lighting[1]),
            ("lighting_2", section.lighting[2]),
        ):
            if plane is None:
                samples.append(Sample(name, None, None, 0))
                continue

            packed = name != "blocks"
            byte_index = index // 2 if packed else index
            byte = plane.data[byte_index] if byte_index < len(plane.data) else None
            value = (byte >> (4 * (index & 1))) & 15 if packed and byte is not None else byte
            half: Literal["low", "high"] | None = ("high" if index & 1 else "low") if packed else None
            samples.append(Sample(name, plane.offset + byte_index, byte, value, half))

        low, metadata, addition = (sample.value for sample in samples[:3])
        state = (
            State(low | (addition << 8) | (metadata << 12))
            if low is not None and metadata is not None and addition is not None
            else None
        )
        biome_index = z * 16 + x
        biome = self.biomes.data[biome_index] if biome_index < len(self.biomes.data) else None
        samples.append(Sample("biome", self.biomes.offset + biome_index, biome, biome))

        return Block(
            position, world, y // 16, index, "stored" if state is not None else "unavailable", state, tuple(samples)
        )
