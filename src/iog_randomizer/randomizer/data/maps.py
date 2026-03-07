from typing import Mapping, Any

# Enemy map database
# FORMAT: { ID: [0: EnemySet,
#                1: RewardBoss(0 for no reward),
#                2: Reward[type, tier],
#                3: FriendlyName,
#                4: DarknessAllowedType (0 = never, 1 = cursed, 2 = possible, 3 = source, 4 = inherited),
#                5: FirstMonsterId,
#                6: LastMonsterId,
#                7: ForbiddenEnemysets,
#                8: Jumbo map (room clear is frustrating or requires multiple visits),
#                9: DarknessSinkMaps
#               ] }
MAPS: Mapping[int, list[Any]] = {
    # TODO: Gets mutated, Consider turning into a class [int, int, list[int], str, int, int, int, list[int], bool, list[int]]
    # Underground Tunnel
    12: [0, 1, [0, 0], "EdDg Entrance", 2, 0x0001, 0x0003, [], False, [13]],
    13: [0, 1, [0, 0], "EdDg East", 2, 0x0004, 0x0012, [6, 10], False, [12, 14]],
    14: [0, 1, [0, 0], "EdDg South", 2, 0x0013, 0x0021, [6, 10], False, [13, 15]],
    15: [0, 1, [0, 0], "EdDg West", 2, 0x0022, 0x002e, [10], False, [14, 17]],
    17: [-1, 0, [0, 0], "EdDg Flower", 4, 0, 0, [], False, [15, 18]],
    18: [0, 1, [0, 0], "EdDg Big", 3, 0x002f, 0x0044, [6, 10], True, [17]],

    # Inca Ruins
    27: [1, 0, [0, 0], "Moon Tribe Cave", 3, 0x0045, 0x004a, [10], False, []],
    29: [1, 1, [0, 0], "Inca Exterior", 1, 0x004b, 0x0059, [10], True, [31, 32, 33, 34, 35, 37, 38]],
    30: [-1, 0, [0, 0], "Inca Near Castoth", 4, 0, 0, [], False, [34, 41]],
    31: [-1, 0, [0, 0], "Inca Statue Puzzle", 2, 0, 0, [], False, [29, 40]],
    32: [1, 1, [0, 0], "Inca Will Ability", 1, 0x005e, 0x0065, [], False, [29, 35]],
    33: [2, 1, [0, 0], "Inca Water", 1, 0x0066, 0x007a, [6, 10], True, [29, 35]],
    34: [2, 1, [0, 0], "Inca Big", 2, 0x007b, 0x008e, [], True, [29, 30, 38]],
    35: [2, 1, [0, 0], "Inca E/W Jump", 1, 0x008f, 0x009d, [6, 10], False, [29, 32, 33]],
    # 36: [-1,0, [0,0], "Inca Golden Tile",    2, 0,      0,      [], False, [34,30]],
    37: [1, 1, [0, 0], "Inca D.Block", 1, 0x009e, 0x00a9, [], False, [29, 39]],
    38: [1, 1, [0, 0], "Inca Divided", 3, 0x00aa, 0x00b3, [], True, [29, 34]],
    39: [1, 1, [0, 0], "Inca West of D.Block", 2, 0x00b4, 0x00c4, [], False, [37]],
    40: [1, 1, [0, 0], "Inca Before Melody", 3, 0x00c5, 0x00cc, [], False, [31]],
    41: [-1, 0, [0, 0], "Inca Castoth", 3, 0, 0, [], False, [30]],

    # Diamond Mine
    61: [3, 2, [0, 0], "Mine Fences", 3, 0x00ce, 0x00d8, [10], False, [65, 66]],
    62: [3, 2, [0, 0], "Mine Entrance", 1, 0x00d9, 0x00df, [], False, [63]],
    63: [3, 2, [0, 0], "Mine Big", 1, 0x00e0, 0x00f7, [], True, [62, 64, 67]],
    64: [3, 2, [0, 0], "Mine Cave-in", 2, 0x00f8, 0x00fd, [10], False, [63, 65]],
    65: [3, 2, [0, 0], "Mine Friar", 2, 0x00fe, 0x0108, [1, 6, 7, 8, 9, 10, 12, 13], False, [61, 64, 66]],
    # Stationary Grundit
    66: [-1, 0, [0, 0], "Mine Caverns", 4, 0, 0, [], False, []],
    67: [-1, 0, [0, 0], "Mine Elevator", 4, 0, 0, [], False, [66, 63, 68]],
    68: [-1, 0, [0, 0], "Mine End Branch", 4, 0, 0, [], False, [66, 67, 69, 70]],
    69: [3, 2, [0, 0], "Mine Morgue", 3, 0x0109, 0x010e, [], False, [68]],
    70: [3, 2, [0, 0], "Mine Other Key", 3, 0x010f, 0x0117, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12], False,
         [68]],
    71: [-1, 0, [0, 0], "Mine Sam", 4, 0, 0, [], False, [70]],

    # Sky Garden
    76: [-1, 0, [0, 0], "SkGn Entrance", 1, 0, 0, [], False, [77, 79, 81, 83, 85]],
    77: [4, 2, [0, 0], "SkGn NE Top", 2, 0x0118, 0x0129, [], True, [76, 78]],
    78: [5, 2, [0, 0], "SkGn NE Bot", 3, 0x012a, 0x0136, [], True, [77]],
    79: [4, 2, [0, 0], "SkGn SE Top", 2, 0x0137, 0x0143, [], True, [76, 80, 86]],
    80: [5, 2, [0, 0], "SkGn SE Bot", 3, 0x0144, 0x014f, [10], True, [79]],
    81: [4, 2, [0, 0], "SkGn SW Top", 2, 0x0150, 0x015c, [10], False, [76, 82]],
    82: [5, 2, [0, 0], "SkGn SW Bot", 3, 0x015d, 0x0163, [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13], True, [81]],
    83: [4, 2, [0, 0], "SkGn NW Top", 2, 0x0164, 0x0172, [], True, [76, 84]],
    84: [5, 2, [0, 0], "SkGn NW Bot", 3, 0x0173, 0x0182, [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13], True, [83]],
    85: [-1, 0, [0, 0], "SkGn Viper", 3, 0, 0, [], False, [76]],
    86: [-1, 0, [0, 0], "SkGn Blue Room", 4, 0, 0, [], False, [79]],

    # Mu
    95: [6, 3, [0, 0], "Mu NW", 1, 0x0193, 0x01a5, [10], True, [96, 98]],
    96: [6, 3, [0, 0], "Mu NE", 1, 0x01a6, 0x01bf, [7, 8, 9, 12], True, [95, 97]],
    97: [6, 3, [0, 0], "Mu E", 2, 0x01c0, 0x01d9, [7, 8, 9, 12], True, [96, 98]],
    98: [6, 3, [0, 0], "Mu W", 2, 0x01da, 0x01e5, [], True, [95, 97, 100]],
    100: [6, 3, [0, 0], "Mu SW", 2, 0x01e6, 0x01ed, [], True, [98, 101]],
    101: [6, 3, [0, 0], "Mu SE", 3, 0x01ee, 0x01fe, [7, 8, 9, 12], False, [100]],

    # Angel Dungeon
    109: [7, 3, [0, 0], "Angel Entrance", 2, 0x0201, 0x020f, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], True, [110]],
    110: [7, 3, [0, 0], "Angel Second", 2, 0x0210, 0x0222, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], True, [109, 111]],
    111: [7, 3, [0, 0], "Angel Dark", 2, 0x0223, 0x0228, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False, [110, 112]],
    112: [7, 3, [0, 0], "Angel Water", 2, 0x0229, 0x022f, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False, [111, 113]],
    113: [7, 3, [0, 0], "Angel Wind", 2, 0x0230, 0x0231, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False, [112, 114]],
    114: [7, 3, [0, 0], "Angel Final", 3, 0x0232, 0x0242, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False, [113]],

    # Great Wall
    130: [8, 4, [0, 0], "GtWl Entrance", 1, 0x0243, 0x0262, [0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 13], True, [131]],
    131: [8, 4, [0, 0], "GtWl Tall Drop", 1, 0x0263, 0x0277, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], True,
          [130, 133]],
    133: [8, 4, [0, 0], "GtWl Ramps", 1, 0x0278, 0x0291, [0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 13], True,
          [131, 134]],
    134: [8, 4, [0, 0], "GtWl Spin Dash", 1, 0x0292, 0x029a, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False,
          [133, 135]],
    135: [8, 4, [0, 0], "GtWl Friar", 2, 0x029b, 0x02a6, [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13], True,
          [134, 136]],
    136: [8, 4, [0, 0], "GtWl Final", 2, 0x02a7, 0x02b5, [0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 13], True,
          [135, 138]],
    138: [-1, 0, [0, 0], "GtWl Fanger", 3, 0, 0, [], False, [136]],

    # Mt Temple
    160: [9, 4, [0, 0], "Kress Entrance", 1, 0x02b7, 0x02c1, [], False, [161]],
    161: [9, 4, [0, 0], "Kress First DS", 1, 0x02c2, 0x02d9, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], True,
          [160, 162]],
    162: [9, 4, [0, 0], "Kress First Vine", 1, 0x02da, 0x02e7, [7, 11], True, [161, 163, 164, 165]],
    163: [9, 4, [0, 0], "Kress Second DS", 3, 0x02e8, 0x02fb, [], False, [162]],
    164: [9, 4, [0, 0], "Kress West Chest", 3, 0x02fc, 0x0315, [6, 7], True, [162]],
    165: [9, 4, [0, 0], "Kress Two Vines", 2, 0x0316, 0x032d, [7, 11], True, [162, 166, 167, 168]],
    166: [9, 4, [0, 0], "Kress Mushrooms", 3, 0x032e, 0x033c, [], True, [165]],
    167: [9, 4, [0, 0], "Kress Final DS", 3, 0x033d, 0x0363, [7], True, [165]],
    168: [9, 4, [0, 0], "Kress Last Combat", 3, 0x0364, 0x036b, [0, 1, 2, 3, 4, 5, 6, 11, 12, 13], False,
          [165, 169]],
    169: [-1, 0, [0, 0], "Kress Final Chest", 4, 0, 0, [], False, [168]],

    # Ankor Wat
    176: [10, 6, [0, 0], "Wat Exterior", 1, 0x036c, 0x037a, [], True, [177]],
    177: [11, 6, [0, 0], "Wat Outer South", 1, 0x037b, 0x038d, [6, 10], True, [176, 178, 181, 182]],
    178: [11, 6, [0, 0], "Wat Outer East", 1, 0x038e, 0x0398, [6, 10, 12], True, [177, 179]],
    179: [11, 6, [0, 0], "Wat Outer North", 1, 0x0399, 0x039f, [], True, [178, 181]],
    180: [11, 6, [0, 0], "Wat Outer Pit", 0, 0x03a0, 0x03a5, [6, 10, 12], False, []],
    181: [11, 6, [0, 0], "Wat Outer West", 1, 0x03a6, 0x03b0, [], True, [177, 179]],
    182: [10, 6, [0, 0], "Wat Garden", 1, 0x03b1, 0x03d7, [7], True, [177, 183]],
    183: [11, 6, [0, 0], "Wat Inner South", 1, 0x03d8, 0x03e3, [], True, [182, 184, 185, 186]],
    # Earthquaker Golem
    184: [11, 6, [0, 0], "Wat Inner East", 3, 0x03e4, 0x03e9, [2, 6, 10, 12], True, [183]],
    185: [11, 6, [0, 0], "Wat Inner West", 1, 0x03ea, 0x03f1, [], False, [183]],
    186: [10, 6, [0, 0], "Wat Road to Main", 4, 0x03f2, 0x03f6, [], True, [183, 187]],
    187: [11, 6, [0, 0], "Wat Main 1F", 2, 0x03f7, 0x03fc, [], False, [186, 188]],
    188: [11, 6, [0, 0], "Wat Main 2F", 0, 0x03fd, 0x0403, [], False, [187, 189]],
    189: [11, 6, [0, 0], "Wat Main 3F", 3, 0x0404, 0x040e, [], False, [188, 190]],
    190: [11, 6, [0, 0], "Wat Main 4F", 4, 0x040f, 0x0415, [], False, [189, 191]],
    191: [-1, 0, [0, 0], "Wat Spirit", 4, 0, 0, [], False, [190]],

    # Pyramid
    204: [12, 5, [0, 0], "Pyramid Foyer", 1, 0x0416, 0x0417, [], False, [206, 208, 210, 212, 214, 216, 221]],
    206: [12, 5, [0, 0], "Pyramid Room 1A", 2, 0x0418, 0x0423, [], True, [204, 207]],
    207: [12, 5, [0, 0], "Pyramid Room 1B", 3, 0x0424, 0x0431, [], True, [206]],
    208: [12, 5, [0, 0], "Pyramid Room 2A", 2, 0x0432, 0x0439, [], False, [204, 209]],
    209: [12, 5, [0, 0], "Pyramid Room 2B", 3, 0x043a, 0x044c, [], True, [208]],
    210: [12, 5, [0, 0], "Pyramid Room 6A", 2, 0x044d, 0x0462, [], True, [204, 211]],
    211: [12, 5, [0, 0], "Pyramid Room 6B", 3, 0x0463, 0x0473, [], True, [210]],
    212: [12, 5, [0, 0], "Pyramid Room 5A", 2, 0x0474, 0x0483, [], True, [204, 213]],
    213: [12, 5, [0, 0], "Pyramid Room 5B", 3, 0x0484, 0x0497, [], True, [212]],
    214: [12, 5, [0, 0], "Pyramid Room 3A", 2, 0x0498, 0x04a8, [], True, [204, 215]],
    215: [12, 5, [0, 0], "Pyramid Room 3B", 3, 0x04a9, 0x04b8, [1, 7, 10], False, [214]],
    216: [12, 5, [0, 0], "Pyramid Room 4A", 2, 0x04b9, 0x04db, [7], True, [204, 217]],
    217: [12, 5, [0, 0], "Pyramid Room 4B", 2, 0x04dc, 0x04f2, [], True, [216, 219]],
    219: [12, 5, [0, 0], "Pyramid Room 4C", 3, 0x04f3, 0x04f6, [1, 2, 3, 6, 7, 10, 13], False, [217]],
    # Spike elevators
    221: [-1, 0, [0, 0], "Pyramid MQ", 3, 0, 0, [], False, [204]],

    # Jeweler's Mansion
    233: [13, 0, [0, 0], "Mansion", 3, 0x04f9, 0x051e, [7, 10], True, [234]],
    234: [-1, 0, [0, 0], "Solid Arm", 4, 0, 0, [], False, [233]],

    # Babel bosses
    242: [-1, 0, [0, 0], "Babel Castoth", 3, 0, 0, [], False, []],
    243: [-1, 0, [0, 0], "Babel Viper", 3, 0, 0, [], False, []],
    245: [-1, 0, [0, 0], "Babel Fanger", 3, 0, 0, [], False, []],
    246: [-1, 0, [0, 0], "Babel MQ", 3, 0, 0, [], False, []]
}