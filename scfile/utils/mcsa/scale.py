from scfile.consts import Normalization


SCALE: float = 1.0
FACTOR: int = Normalization.I16

def scaled(i: float, scale: float = SCALE, factor: int = FACTOR) -> float:
    # TODO: optional scale and factor.
    return (i * scale) / factor
