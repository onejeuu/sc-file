from collections.abc import Mapping
from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Final

import numpy as np
from numpy.typing import NDArray

from scfile.exceptions import BlockMappingError
from scfile.options import BlockMapping, BlockMappings

from .resourcepack import BLOCKS as RESOURCEPACK
from .vanilla import BLOCKS as VANILLA

RESOURCE_KEY: Final = "mca.mapping"

DEFAULT: Final = "vanilla"
IDENTITY: Final[BlockMapping] = {str(block_id): str(block_id) for block_id in range(256)}
BUILTIN: Final[Mapping[str, BlockMapping]] = MappingProxyType(
    {
        "vanilla": VANILLA,
        "resourcepack": RESOURCEPACK,
        "identity": IDENTITY,
    }
)

BLOCK_ID_BITS = 12
BLOCK_ID_COUNT = 1 << BLOCK_ID_BITS
PRESERVE_METADATA = 16


@dataclass(frozen=True, slots=True)
class CompiledBlockMapping:
    ids: NDArray[np.uint16]
    metadata: NDArray[np.uint8]
    _low_mask: bytes | None
    _low_lut: NDArray[np.uint8] | None
    _metadata_overrides: bool
    _high_targets: bool
    _state_lut: NDArray[np.uint16]
    _tile_locked: NDArray[np.bool_]


def build(mappings: BlockMappings = None) -> tuple[CompiledBlockMapping, bytes | None]:
    mapping = compile(mappings)
    low = mapping.ids[:256]
    byte_mapping = low.astype(np.uint8).tobytes() if np.all(low <= 255) else None
    return mapping, byte_mapping


def compile(mappings: BlockMappings = None) -> CompiledBlockMapping:
    if mappings is None:
        layers = (BUILTIN[DEFAULT],)
    elif isinstance(mappings, Mapping):
        layers = (mappings,)
    else:
        layers = mappings or (BUILTIN[DEFAULT],)

    ids = np.zeros(BLOCK_ID_COUNT, dtype=np.uint16)
    metadata = np.full(BLOCK_ID_COUNT, PRESERVE_METADATA, dtype=np.uint8)
    tile_locked = np.zeros(BLOCK_ID_COUNT, dtype=np.bool_)

    for layer_index, layer in enumerate(layers):
        for source, target in layer.items():
            source_id = _block_id(source, "source", layer_index)
            if not isinstance(target, str):
                raise BlockMappingError(f"Mapping layer {layer_index + 1}: target must be a string.")

            tile_lock = target.endswith("!")
            if tile_lock:
                target = target[:-1]

            target_id_text, separator, metadata_text = target.partition(":")
            target_id = _block_id(target_id_text, "target", layer_index)
            target_meta = _metadata(metadata_text, layer_index) if separator else PRESERVE_METADATA

            ids[source_id] = target_id
            metadata[source_id] = target_meta
            tile_locked[source_id] = tile_lock

    ids.flags.writeable = False
    metadata.flags.writeable = False
    tile_locked.flags.writeable = False

    has_overrides = bool(np.any(metadata != PRESERVE_METADATA))
    low_overrides = metadata[:256] != PRESERVE_METADATA
    low_mask = low_overrides.astype(np.uint8).tobytes() if np.any(low_overrides) else None

    low_lut = None
    if low_mask is not None:
        low_lut = np.broadcast_to(np.arange(16, dtype=np.uint8), (256, 16)).copy()
        low_lut[low_overrides] = metadata[:256][low_overrides, None]
        low_lut.flags.writeable = False

    has_high_targets = bool(np.any(ids > 0xFF))

    source_metadata = np.arange(16, dtype=np.uint16)[:, None]
    mapped_metadata = np.where(
        metadata[None, :] == PRESERVE_METADATA,
        source_metadata,
        metadata[None, :],
    ).astype(np.uint16)
    state_lut = ((mapped_metadata << 12) | ids[None, :]).astype(np.uint16).reshape(-1)
    state_lut.flags.writeable = False

    return CompiledBlockMapping(
        ids,
        metadata,
        low_mask,
        low_lut,
        has_overrides,
        has_high_targets,
        state_lut,
        tile_locked,
    )


_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z")


def _number(value: object, role: str, layer: int, maximum: int) -> int:
    if not isinstance(value, str) or _DECIMAL.fullmatch(value) is None:
        raise BlockMappingError(f"Mapping layer {layer + 1}: {role} must be a decimal string.")

    if len(value) > len(str(maximum)):
        raise BlockMappingError(f"Mapping layer {layer + 1}: {role} {value} is outside 0..{maximum}.")

    number = int(value)
    if number > maximum:
        raise BlockMappingError(f"Mapping layer {layer + 1}: {role} {number} is outside 0..{maximum}.")
    return number


def _block_id(value: object, role: str, layer: int) -> int:
    return _number(value, f"{role} block ID", layer, BLOCK_ID_COUNT - 1)


def _metadata(value: object, layer: int) -> int:
    return _number(value, "target metadata", layer, 15)
