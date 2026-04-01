BLOCKS: dict[int, int] = {
    # Barrier
    178: 166,  # daylight sensor
    # Air
    88: 0,  # soul sand -> (light)
    89: 0,  # glowstone -> (light)
    39: 0,  # mushroom -> (therma?)
    117: 0,  # brewing stand
    180: 0,  # red sandstone stairs -> slab
    114: 0,  # nether stairs -> slab
    111: 0,  # lily pad -> slab
    40: 0,  # red mushroom
    127: 0,  # cocoa
    251: 0,  # white concrete
    255: 0,  # structure block
    223: 0,  # yellow shulker
    113: 0,  # nether fence
    123: 0,  # lamp (off)
    124: 0,  # lamp (on)
    193: 0,  # spruce door
    129: 0,  # emerald ore
    # Stone
    183: 1,  # spruce
    101: 1,  # iron bars
    203: 1,  # purpur stairs
    27: 1,  # power rail
    90: 1,  # nether portal
    119: 1,  # end portal
    # Grass
    141: 2,  # carrots
    # Dirt
    143: 3,  # wood button
    142: 3,  # potatos
    54: 3,  # chest
    146: 3,  # trap chest
    # Cobblestone
    149: 4,  # comporator (off)
    128: 4,  # sandstone stairs
    28: 4,  # detector rail
    # Planks
    99: 5,  # mushroom block
    # Water
    179: 9,  # red sandstone
    # Wool
    198: 35,  # end rod
    62: 35,  # furnace (on)
    # Bricks
    250: 45,  # black glazed
    # Obsidian
    181: 49,  # double red sandstone slab
    201: 49,  # purpur block
    202: 49,  # purpur pillar
    230: 49,  # blue shulker
    53: 49,  # oak stairs
    61: 49,  # furnace (off)
    50: 49,  # torch
    # Diamond
    66: 57,  # rail
    # Ladder
    109: 65,  # stone bricks stairs
    # Netherrack
    194: 87,  # birch door
    # Grass Deadbush
    132: 32,  # tripline
    133: 32,  # emerald
    214: 32,  # wart block
    226: 32,  # gray shulker
    244: 32,  # cyan glazed
    248: 32,  # green glazed
    # Grass Dandelion
    213: 37,  # magma
    216: 37,  # bone block
    225: 37,  # pink shulker
    227: 37,  # light gray shulker
    245: 37,  # purple glazed
    246: 37,  # blue glazed
    252: 37,  # white powder
    # Grass Poppy
    116: 38,  # enchantment table
    118: 38,  # cauldron
    121: 38,  # endstone
    122: 38,  # dragon egg
    210: 38,  # command block (repeat)
    211: 38,  # command block (chain)
    240: 38,  # lime glazed
    241: 38,  # pink glazed
    242: 38,  # gray glazed
    247: 38,  # brown glazed
    # Grass Canes
    212: 83,  # forsted ice
    215: 83,  # red nether bricks
    221: 83,  # magenta shulker
    222: 83,  # magenta shulker
    228: 83,  # cyan shulker
    229: 83,  # shulker
    249: 83,  # red glazed
    # Grass Mushroom
    243: 39,  # light gray glazed
    # Vines
    236: 106,  # orange glazed
    237: 106,  # magenta glazed
    238: 106,  # light blue glazed
    239: 106,  # yellow glazed
    # Nether Bricks
    182: 112,  # red sandstone slab
    # Gates -> Fences
    107: 85,  # oak
    189: 113,  # birch fence
    184: 189,  # birch
    185: 190,  # jungle
    186: 191,  # dark oak
    187: 192,  # acacia
}


def build_blocks_mapping(mapping: dict[int, int]) -> bytes:
    table = list(range(256))

    for old, new in mapping.items():
        table[old] = new

    return bytes(table)


BLOCKS_MAPPING = build_blocks_mapping(BLOCKS)
