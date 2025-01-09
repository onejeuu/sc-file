from typing import TypeAlias


Mask: TypeAlias = tuple[int, int, int, int]

R = 0x000000FF
G = 0x0000FF00
B = 0x00FF0000
A = 0xFF000000

RGBA8: Mask = (R, G, B, A)
BGRA8: Mask = (B, G, R, A)
