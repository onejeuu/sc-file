class BITMASK:
    RGBA8 = [0xFF, 0xFF00, 0xFF0000, 0xFF]
    BGRA8 = [0xFF, 0x00FF, 0x0000FF, 0x000000FF]

    def __init__(self, fourcc: bytes):
        self.fourcc = fourcc

    def __iter__(self):
        match self.fourcc:
            case b"RGBA8":
                return iter(BITMASK.RGBA8)

            case b"BGRA8":
                return iter(BITMASK.BGRA8)

            case _:
                return iter(BITMASK.RGBA8)
