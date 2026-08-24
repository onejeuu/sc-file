import numpy as np

from .mapping import STATE_MAPPING


SECTION_SIZE = 16 * 16 * 16


def section(
    blocks: memoryview,
    metadata: memoryview,
    additions: memoryview,
    raw: bool,
) -> tuple[bytes, bytes, bytes]:
    meta = _unpack(metadata)
    add = _unpack(additions)
    states = np.frombuffer(blocks, dtype=np.uint8).astype(np.uint16)
    states |= add << 8
    states |= meta << 12

    if not raw:
        states = STATE_MAPPING[states]

    return (
        (states & 0xFF).astype(np.uint8).tobytes(),
        _pack(states >> 12),
        _pack(states >> 8),
    )


def _unpack(
    data: memoryview,
) -> np.ndarray:
    packed = np.frombuffer(data, dtype=np.uint8)
    values = np.zeros(SECTION_SIZE, dtype=np.uint16)
    size = packed.size * 2
    values[:size:2] = packed & 0xF
    values[1:size:2] = packed >> 4
    return values


def _pack(
    values: np.ndarray,
) -> bytes:
    packed = values[::2] | (values[1::2] << 4)
    return packed.astype(np.uint8).tobytes()
