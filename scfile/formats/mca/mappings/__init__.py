from types import MappingProxyType
from typing import Final


from collections.abc import Mapping
from numbers import Integral

import numpy as np
from numpy.typing import NDArray

from scfile.exceptions import BlockMappingError
from scfile.options import BlockMappings

from .resourcepack import BLOCKS as RESOURCEPACK
from .vanilla import BLOCKS as VANILLA

RESOURCE_KEY: Final = "mca.mapping"
DEFAULT_MAPPING: Final = "resourcepack"
BUILTIN_MAPPINGS = MappingProxyType(
    {
        "vanilla": VANILLA,
        "resourcepack": RESOURCEPACK,
    }
)


BLOCK_ID_BITS = 12
BLOCK_ID_COUNT = 1 << BLOCK_ID_BITS


type CompiledBlockMapping = NDArray[np.uint16]


def build(mappings: BlockMappings = None) -> tuple[CompiledBlockMapping, bytes | None]:
    mapping = compile(mappings)
    low = mapping[:256]
    byte_mapping = low.astype(np.uint8).tobytes() if np.all(low <= 255) else None
    return mapping, byte_mapping


def compile(mappings: BlockMappings = None) -> CompiledBlockMapping:
    if mappings is None:
        layers = (BUILTIN_MAPPINGS[DEFAULT_MAPPING],)
    elif isinstance(mappings, Mapping):
        layers = (mappings,)
    else:
        layers = mappings or (BUILTIN_MAPPINGS[DEFAULT_MAPPING],)

    table = np.zeros(BLOCK_ID_COUNT, dtype=np.uint16)

    for layer_index, layer in enumerate(layers):
        for source, target in layer.items():
            source_id = _block_id(source, "source", layer_index)
            target_id = _block_id(target, "target", layer_index)
            table[source_id] = target_id

    table.flags.writeable = False
    return table


def _block_id(value: object, role: str, layer: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise BlockMappingError(f"Mapping layer {layer + 1}: {role} block ID must be an integer.")

    block_id = int(value)
    if not 0 <= block_id < BLOCK_ID_COUNT:
        raise BlockMappingError(
            f"Mapping layer {layer + 1}: {role} block ID {block_id} is outside 0..{BLOCK_ID_COUNT - 1}."
        )

    return block_id
