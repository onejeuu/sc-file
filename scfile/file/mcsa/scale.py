from scfile.consts import Factor


SCALE: float = 1.0
FACTOR: int = Factor.I16

def scaled(i: float, scale: float = SCALE, factor: int = FACTOR) -> float:
    return (i * scale) / factor
