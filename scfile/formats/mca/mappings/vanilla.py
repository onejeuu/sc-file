BLOCKS: dict[int, int] = {
    # ! Vanilla compatible
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    9: 9,
    11: 11,
    12: 12,
    13: 13,
    17: 17,
    18: 18,
    20: 20,
    24: 24,
    31: 31,
    32: 32,
    35: 35,
    37: 37,
    38: 38,
    42: 42,
    45: 45,
    47: 47,
    48: 48,
    49: 49,
    50: 50,
    53: 53,
    57: 57,
    65: 65,
    67: 67,
    69: 69,
    71: 71,
    75: 75,
    78: 78,
    79: 79,
    82: 82,
    89: 89,
    96: 96,
    98: 98,
    101: 101,
    106: 106,
    108: 108,
    109: 109,
    112: 112,
    123: 123,
    153: 153,
    155: 155,
    159: 159,
    172: 172,
    # ! Palette substitutions
    7: 173,  # rubber -> coal block
    14: 41,  # yellow tile -> gold block
    15: 42,  # white tile -> iron block
    16: 1,  # concrete -> stone
    19: 170,  # sandbags -> hay bale
    21: 18,  # green fabric -> leaves
    22: 18,  # camouflage fabric -> leaves
    39: 30,  # net -> cobweb
    40: 30,
    41: 45,  # red metal -> bricks
    56: 42,  # beige metal -> iron block
    73: 22,  # blue metal -> lapis block
    74: 22,
    80: 173,  # rubber variant -> coal block
    85: 5,  # plank texture -> planks
    87: 49,  # bitumen rock -> obsidian
    86: 25,  # television casing -> note block
    88: 12,  # sand variant -> sand
    91: 25,
    99: 18,  # camouflage net blocks -> leaves
    100: 18,
    102: 20,  # glass -> glass
    103: 173,  # wheel texture -> coal block
    110: 3,  # dirt variant -> dirt
    113: 101,  # rusty fence -> iron bars
    121: 41,  # beige metal -> gold block
    129: 42,  # marked metal -> iron block
    133: 5,  # plank texture -> planks
    152: 1,  # concrete -> stone
    156: 101,  # metal construction -> iron bars
    170: 152,  # electronics -> redstone block
    # ! ProBuilder geometry markers
    2401: 1,  # generic slope
    2402: 67,  # stairs -> cobblestone stairs
    2403: 85,  # fence -> fence
    2405: 1,  # cube / half-block
    2413: 109,  # stairs -> stone-brick stairs
    2414: 44,  # half-block -> stone slab
    2415: 2,  # grass slope
    2416: 3,  # dirt slope
    2417: 13,  # gravel slope
    2418: 12,  # sand slope
    2420: 3,  # dirt2 slope
    2421: 49,  # dark rock slope -> obsidian
    2423: 82,  # clay slope
    2445: 2,  # double grass slope
    2446: 3,
    2447: 13,
    2448: 12,
    2450: 3,
    2451: 49,
    2453: 82,
    2480: 1,  # 1/8 block
    2481: 44,  # half step
    2484: 1,  # triangle
    2486: 1,  # collapsible block; exact cover is stored in records
    2487: 1,  # 3/4 cube
    2488: 44,  # quarter slab
    2489: 44,  # quarter beam
    2490: 1,
    2491: 1,
    2493: 1,
    2494: 1,
    2495: 1,
    2496: 1,
    2497: 1,
    2498: 1,  # ProBuilder occupancy marker
    # ! Custom construction blocks
    3500: 1,  # generic block
    3514: 173,  # black block
    3519: 45,  # dark red masonry
    3526: 133,  # green block -> emerald block
    3530: 42,  # lock hardware
    3531: 42,
    3546: 42,
    3558: 1,  # rock
    3560: 155,  # light paving -> quartz block
    3573: 5,  # mossy wood
    3580: 17,  # logs
    # ! Vegetation models
    3700: 38,  # red poppy
    3702: 37,  # chamomile -> dandelion
    3709: 31,  # small vegetation
    3710: 31,
    3711: 31,
    3712: 31,
    3716: 31,
    3717: 31,
    3796: 31,
    3797: 31,
    3798: 31,
    3799: 31,
    3800: 31,
    3805: 31,  # fern variants
    3806: 31,
    3807: 31,
    3809: 31,
    3810: 31,
    3811: 31,
    3812: 31,
    3813: 31,
    3820: 106,  # liana -> vine
    3821: 106,
    3822: 106,
    3824: 31,
    3825: 31,
    3826: 31,
    3829: 83,  # reeds
    3830: 83,
    3831: 83,  # cattails
    3832: 83,
    3834: 83,
    3835: 83,  # water variants
    3836: 83,
    3837: 83,
    3838: 83,
    3840: 83,
    3874: 31,  # fern
    3875: 31,  # tall grass
    # ! Invisible markers and non-rendering blocks
    3928: 0,
    3930: 0,
    3999: 0,
    4018: 0,
    4025: 0,
    4026: 0,
}
