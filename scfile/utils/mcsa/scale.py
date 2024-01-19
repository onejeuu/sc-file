from scfile.consts import Normalization


SCALE: float = 1.0
FACTOR: int = Normalization.I16
ROUND: int = 8

def scaled(i: float, scale: float = SCALE, factor: int = FACTOR, digits: int = ROUND) -> float:
    return round((i * scale) / factor, digits)
