from typing import Mapping, Any

# Define Item/Ability/Statue locations
# Format: { ID: [0: Parent Node,
#                1: Type (1=item, 2=ability, 3=statue, 4=game state, 5=monster orb, 6=artificial),
#                2: Filled Flag,
#                3: Filled Item (default listed here, which is cleared or hardened on init),
#                4: [Restricted Items],
#                5: ASM ID label (if applicable),
#                6: Name,
#                7: ShufflePool (populated during world initialization),
#                8: DiscoveredCycle (populated during item placement),
#                9: CollectionLogic (a form=0 reqset as in self.logic; for more complex logic, use a real node)
#               ] }
ITEM_LOCATIONS: Mapping[int, list[Any]] = {
    # TODO: Gets mutated, Consider turning into a class [int, int, bool, int, list[int], str, str, int, int, list[int]]
    # Jeweler
    0: [2, 1, False, 0, [], "Jeweler1Item", "Jeweler Reward 1", 0, 0, []],
    1: [3, 1, False, 0, [], "Jeweler2Item", "Jeweler Reward 2", 0, 0, []],
    2: [4, 1, False, 0, [], "Jeweler3Item", "Jeweler Reward 3", 0, 0, []],
    3: [5, 1, False, 0, [], "Jeweler4Item", "Jeweler Reward 4", 0, 0, []],
    4: [6, 1, False, 0, [], "Jeweler5Item", "Jeweler Reward 5", 0, 0, []],
    5: [7, 1, False, 0, [], "Jeweler6Item", "Jeweler Reward 6", 0, 0, []],

    # South Cape
    6: [21, 1, False, 0, [], "CapeTowerItem", "South Cape: Bell Tower", 0, 0, []],
    7: [20, 1, False, 0, [], "CapeFisherItem", "South Cape: Fisherman", 0, 0, []],
    8: [26, 1, False, 0, [], "CapeLancesHouseItem", "South Cape: Lance's House", 0, 0, []],
    9: [23, 1, False, 0, [], "CapeLolaItem", "South Cape: Lola", 0, 0, []],

    10: [21, 2, False, 0, [], "", "South Cape: Dark Space", 0, 0, []],

    # Edward's
    11: [30, 1, False, 0, [], "ECHiddenGuardItem", "Edward's Castle: Hidden Guard", 0, 0, []],
    12: [30, 1, False, 0, [], "ECBasementItem", "Edward's Castle: Basement", 0, 0, []],
    13: [32, 1, False, 0, [], "EDHamletItem", "Edward's Prison: Hamlet", 0, 0, []],

    14: [32, 2, False, 0, [], "", "Edward's Prison: Dark Space", 0, 0, []],

    # Underground Tunnel
    15: [39, 1, False, 0, [], "EDSpikeChestItem", "Underground Tunnel: Spike's Chest", 0, 0, []],
    16: [44, 1, False, 0, [], "EDSmallRoomChestItem", "Underground Tunnel: Small Room Chest", 0, 0, []],
    17: [705, 1, False, 0, [], "EDEndChestItem", "Underground Tunnel: Ribber's Chest  ", 0, 0, []],
    18: [49, 1, False, 0, [], "EDEndBarrelsItem", "Underground Tunnel: Barrels", 0, 0, []],

    19: [720, 2, False, 0, [], "", "Underground Tunnel: Dark Space", 0, 0, []],

    700: [41, 5, False, 0, [], "EDCageWormItem", "Underground Tunnel: Worm for East Skeleton Cage", 0, 0,
          [[609, 1]]],
    701: [41, 5, False, 0, [], "EDSoutheastWormItem", "Underground Tunnel: Worm for East Door", 0, 0,
          [[609, 1]]],
    702: [42, 5, False, 0, [], "EDSouthwestWormItem", "Underground Tunnel: Worm for South Door", 0, 0,
          [[609, 1]]],
    703: [43, 5, False, 0, [], "EDDoorBatItem", "Underground Tunnel: Bat for West Door", 0, 0, [[609, 1]]],
    704: [47, 5, False, 0, [], "EDDarkSpaceWormItem", "Underground Tunnel: Worm for Appearing Dark Space", 0, 0,
          [[609, 1]]],
    705: [704, 5, False, 0, [], "EDSkeleton1Item", "Underground Tunnel: Red Skeleton 1", 0, 0, [[609, 1]]],
    706: [705, 5, False, 0, [], "EDSkeleton2Item", "Underground Tunnel: Red Skeleton 2", 0, 0, [[609, 1]]],

    # Itory
    20: [51, 1, False, 0, [], "ItoryLogsItem", "Itory Village: Logs", 0, 0, []],
    21: [58, 1, False, 0, [], "ItoryCaveItem", "Itory Village: Cave", 0, 0, []],

    22: [51, 2, False, 0, [], "", "Itory Village: Dark Space", 0, 0, []],

    # Moon Tribe
    23: [62, 1, False, 0, [], "MoonTribeCaveItem", "Moon Tribe: Cave", 0, 0, []],

    # Inca
    24: [71, 1, False, 0, [], "IncaDiamondBlockChestItem", "Inca Ruins: Diamond-Block Chest", 0, 0, []],
    25: [92, 1, False, 0, [], "IncaMazeChestItem", "Inca Ruins: Broken Statues Chest", 0, 0, []],
    26: [83, 1, False, 0, [], "IncaStatueChestItem", "Inca Ruins: Stone Lord Chest", 0, 0, []],
    27: [93, 1, False, 0, [], "IncaWormChestItem", "Inca Ruins: Slugger Chest", 0, 0, []],
    28: [76, 1, False, 0, [], "IncaCliffItem", "Inca Ruins: Singing Statue", 0, 0, []],

    29: [96, 2, False, 0, [], "", "Inca Ruins: Dark Space 1", 0, 0, []],
    30: [93, 2, False, 0, [], "", "Inca Ruins: Dark Space 2", 0, 0, []],
    31: [77, 2, False, 0, [], "", "Inca Ruins: Final Dark Space", 0, 0, []],

    707: [700, 5, False, 0, [], "IncaWestLadderItem", "Inca Ruins: 4-Way for West Ladder", 0, 0, [[609, 1]]],
    708: [75, 5, False, 0, [], "IncaSoutheastLadderItem", "Inca Ruins: 4-Way for SE Ladder", 0, 0, [[609, 1]]],
    709: [72, 5, False, 0, [], "IncaNortheastLadderItem", "Inca Ruins: 4-Way for NE Ladder", 0, 0, [[609, 1]]],
    710: [82, 5, False, 0, [], "IncaNSRampItem", "Inca Ruins: Whirligig for N/S Ramp", 0, 0, [[609, 1]]],
    711: [707, 5, False, 0, [], "IncaEWRampItem", "Inca Ruins: Whirligig for E/W Ramp", 0, 0, [[609, 1]]],
    712: [94, 5, False, 0, [], "IncaDBlockMonsterItem", "Inca Ruins: 4-Way West of Diamond Block Room", 0, 0,
          [[609, 1]]],
    713: [96, 5, False, 0, [], "IncaWMelodyMonsterItem", "Inca Ruins: 4-Way Before Singing Statue", 0, 0,
          [[609, 1]]],

    # Gold Ship
    32: [100, 1, False, 0, [], "IncaGoldShipItem", "Gold Ship: Seth", 0, 0, []],

    # Diamond Coast
    33: [102, 1, False, 0, [], "DiamondCoastJarItem", "Diamond Coast: Jar", 0, 0, []],

    # Freejia
    34: [121, 1, False, 0, [], "FrejHotelItem", "Freejia: Hotel", 0, 0, []],
    35: [110, 1, False, 0, [], "FrejEastSlaverItem", "Freejia: Creepy Guy", 0, 0, []],
    36: [110, 1, False, 0, [], "FrejBin1Item", "Freejia: Trash Can 1", 0, 0, []],
    37: [110, 1, False, 0, [], "FrejBin2Item", "Freejia: Trash Can 2", 0, 0, []],
    38: [110, 1, False, 0, [], "FrejSnitchItem", "Freejia: Snitch", 0, 0, [[504, 1]]],

    39: [125, 2, False, 0, [], "", "Freejia: Dark Space", 0, 0, []],

    # Diamond Mine
    40: [134, 1, False, 0, [], "MineChestItem", "Diamond Mine: Chest", 0, 0, []],
    41: [136, 1, False, 0, [], "MineWallSlaveItem", "Diamond Mine: Trapped Laborer", 0, 0, [[608, 1]]],
    42: [143, 1, False, 0, [], "MineRampSlaveItem", "Diamond Mine: Laborer w/Elevator Key", 0, 0, [[609, 1]]],
    43: [148, 1, False, 0, [], "MineMorgueItem", "Diamond Mine: Morgue", 0, 0, []],
    44: [149, 1, False, 0, [], "MineCombatSlaveItem", "Diamond Mine: Laborer w/Mine Key", 0, 0, [[609, 1]]],
    45: [150, 1, False, 0, [], "MineSamItem", "Diamond Mine: Sam", 0, 0, [[609, 1]]],

    46: [721, 2, False, 0, [], "", "Diamond Mine: Appearing Dark Space", 0, 0, []],
    47: [131, 2, False, 0, [], "", "Diamond Mine: Dark Space at Wall", 0, 0, []],
    48: [142, 2, False, 0, [], "", "Diamond Mine: Dark Space behind Wall", 0, 0, []],

    714: [701, 5, False, 0, [], "MineMidFenceItem", "Diamond Mine: Lizard for Tunnel Middle Fence", 0, 0,
          [[609, 1]]],
    715: [130, 5, False, 0, [], "MineSouthFenceItem", "Diamond Mine: Eye for Tunnel South Fence", 0, 0,
          [[609, 1]]],
    716: [709, 5, False, 0, [], "MineNorthFenceItem", "Diamond Mine: Eye for Tunnel North Fence", 0, 0,
          [[609, 1]]],
    717: [134, 5, False, 0, [], "MineWormCageItem", "Diamond Mine: Worm for Big Room Cage", 0, 0, [[609, 1]]],
    718: [136, 5, False, 0, [], "MineWormDarkSpaceItem", "Diamond Mine: Worm for Appearing Dark Space", 0, 0,
          [[609, 1]]],
    719: [710, 5, False, 0, [], "MineFriarFenceItem", "Diamond Mine: Worm for Friar Ramp Fence", 0, 0,
          [[609, 1]]],

    # Sky Garden
    49: [172, 1, False, 0, [], "SGNENorthChestItem", "Sky Garden: (NE) Platform Chest", 0, 0, []],
    50: [173, 1, False, 0, [], "SGNEWestChestItem", "Sky Garden: (NE) Blue Cyber Chest", 0, 0, []],
    51: [174, 1, False, 0, [], "SGNEStatueChestItem", "Sky Garden: (NE) Statue Chest", 0, 0, []],
    52: [716, 1, False, 0, [], "SGSEChestItem", "Sky Garden: (SE) Dark Side Chest", 0, 0, []],
    53: [185, 1, False, 0, [], "SGSWTopChestItem", "Sky Garden: (SW) Ramp Chest", 0, 0, []],
    54: [186, 1, False, 0, [], "SGSWBotChestItem", "Sky Garden: (SW) Dark Side Chest", 0, 0, []],
    55: [194, 1, False, 0, [], "SGNWTopChestItem", "Sky Garden: (NW) North Chest", 0, 0, []],
    56: [194, 1, False, 0, [], "SGNWBotChestItem", "Sky Garden: (NW) South Chest", 0, 0, [[609, 1]]],

    57: [170, 2, False, 0, [], "", "Sky Garden: Dark Space (Foyer)", 0, 0, []],
    58: [169, 2, False, 0, [], "", "Sky Garden: Dark Space (SE)", 0, 0, []],
    59: [183, 2, False, 0, [], "", "Sky Garden: Dark Space (SW)", 0, 0, []],
    60: [195, 2, False, 0, [], "", "Sky Garden: Dark Space (NW)", 0, 0, []],

    720: [711, 5, False, 0, [], "SGSETopBarrierItem", "Sky Garden: (SE) Top Robot for Center Barrier", 0, 0,
          [[609, 1]]],
    721: [180, 5, False, 0, [], "SGSEBotBarrierItem", "Sky Garden: (SE) Bottom Robot for Chest", 0, 0,
          [[609, 1]]],
    722: [181, 5, False, 0, [], "SGSWTopPegGateItem", "Sky Garden: (SW) Top Robot for Peg Gate", 0, 0,
          [[609, 1]]],
    723: [168, 5, False, 0, [], "SGSWTopRobotRampItem", "Sky Garden: (SW) Top Robot for Robot Ramp", 0, 0,
          [[609, 1]]],
    724: [182, 5, False, 0, [], "SGSWTopWormGateItem", "Sky Garden: (SW) Top Worm for West Gate", 0, 0,
          [[609, 1]]],
    725: [187, 5, False, 0, [], "SGSWBotFireCageItem", "Sky Garden: (SW) Bot Robot for Fire Cages", 0, 0,
          [[609, 1]]],

    # Seaside Palace
    61: [202, 1, False, 0, [], "SeaPalSideChestItem", "Seaside Palace: Side Room Chest", 0, 0, []],
    62: [200, 1, False, 0, [], "SeaPalTopChestItem", "Seaside Palace: First Area Chest", 0, 0, []],
    63: [205, 1, False, 0, [], "SeaPalBotChestItem", "Seaside Palace: Second Area Chest", 0, 0, []],
    64: [200, 1, False, 0, [], "SeaPalBuffyItem", "Seaside Palace: Buffy", 0, 0, [[510, 1]]],
    65: [205, 1, False, 0, [], "SeaPalCoffinItem", "Seaside Palace: Coffin", 0, 0, [[501, 1]]],

    66: [200, 2, False, 0, [], "", "Seaside Palace: Dark Space", 0, 0, []],

    # Mu
    67: [217, 1, False, 0, [], "MuEmptyChest1Item", "Mu: Empty Chest 1", 0, 0, [[609, 1]]],
    68: [220, 1, False, 0, [], "MuEmptyChest2Item", "Mu: Empty Chest 2", 0, 0, []],
    69: [225, 1, False, 0, [], "MuHopeStatue1Item", "Mu: Hope Statue 1", 0, 0, []],
    70: [236, 1, False, 0, [], "MuHopeStatue2Item", "Mu: Hope Statue 2", 0, 0, []],
    71: [215, 1, False, 0, [], "MuHopeRoomChestItem", "Mu: Chest s/o Hope Room 2", 0, 0, []],
    72: [214, 1, False, 0, [], "MuRamaChestNItem", "Mu: Rama Chest N", 0, 0, []],
    73: [219, 1, False, 0, [], "MuRamaChestEItem", "Mu: Rama Chest E", 0, 0, [[609, 1]]],

    74: [218, 2, False, 0, [], "", "Mu: Northeast Dark Space", 0, 0, []],
    75: [228, 2, False, 0, [], "", "Mu: Slider Dark Space", 0, 0, []],

    726: [212, 5, False, 0, [], "MuEntranceGolemItem", "Mu: Entrance Golem for Gate", 0, 0, [[609, 1]]],
    727: [726, 5, False, 0, [], "MuDroplet1Item", "Mu: NE Droplet for Rock 1", 0, 0, [[609, 1]]],
    728: [724, 5, False, 0, [], "MuDroplet2Item", "Mu: NE Droplet for Rock 2", 0, 0, [[609, 1]]],
    729: [227, 5, False, 0, [], "MuSlimeCageItem", "Mu: West Slime for Slime Cages", 0, 0, [[609, 1]]],
    730: [236, 5, False, 0, [], "MuEastFacingHeadGolemItem", "Mu: SE Golem for East-facing Head", 0, 0,
          [[609, 1]]],
    731: [236, 5, False, 0, [], "MuSouthFacingHeadGolemItem", "Mu: SE Golem for South-facing Head", 0, 0,
          [[609, 1]]],

    # Angel Village
    76: [254, 1, False, 0, [], "AnglDanceHallItem", "Angel Village: Dance Hall", 0, 0, []],
    77: [255, 2, False, 0, [], "", "Angel Village: Dark Space", 0, 0, []],

    # Angel Dungeon
    78: [265, 1, False, 0, [], "AnglSliderChestItem", "Angel Dungeon: Slider Chest", 0, 0, []],
    79: [271, 1, False, 0, [], "AnglIshtarSidePotItem", "Angel Dungeon: Ishtar's Room", 0, 0, []],
    80: [274, 1, False, 0, [], "AnglPuzzleChest1Item", "Angel Dungeon: Puzzle Chest 1", 0, 0, []],
    81: [274, 1, False, 0, [], "AnglPuzzleChest2Item", "Angel Dungeon: Puzzle Chest 2", 0, 0, []],
    82: [273, 1, False, 0, [], "AnglIshtarWinChestItem", "Angel Dungeon: Ishtar's Chest", 0, 0, []],

    # Watermia
    83: [280, 1, False, 0, [], "WtrmWestJarItem", "Watermia: West Jar", 0, 0, []],
    85: [286, 1, False, 0, [], "WtrmLanceItem", "Watermia: Lance", 0, 0, []],
    86: [283, 1, False, 0, [], "WtrmDesertJarItem", "Watermia: Gambling House", 0, 0, []],
    87: [280, 1, False, 0, [], "WtrmRussianGlassItem", "Watermia: Russian Glass", 0, 0, []],

    88: [282, 2, False, 0, [], "", "Watermia: Dark Space", 0, 0, []],

    # Great Wall
    89: [290, 1, False, 0, [], "GtWlNecklace1Item", "Great Wall: Necklace 1", 0, 0, []],
    90: [292, 1, False, 0, [], "GtWlNecklace2Item", "Great Wall: Necklace 2", 0, 0, []],
    91: [292, 1, False, 0, [], "GtWlChest1Item", "Great Wall: Chest 1", 0, 0, []],
    92: [294, 1, False, 0, [], "GtWlChest2Item", "Great Wall: Chest 2", 0, 0, []],

    93: [295, 2, False, 0, [], "", "Great Wall: Archer Dark Space", 0, 0, []],
    94: [297, 2, False, 0, [], "", "Great Wall: Platform Dark Space", 0, 0, []],
    95: [300, 2, False, 0, [], "", "Great Wall: Appearing Dark Space", 0, 0, []],

    732: [712, 5, False, 0, [], "GtWlArcherItem", "Great Wall: Archer for Friar Gate", 0, 0, [[609, 1]]],

    # Euro
    96: [310, 1, False, 0, [], "EuroAlleyItem", "Euro: Alley", 0, 0, []],
    97: [310, 1, False, 0, [], "EuroAppleVendorItem", "Euro: Apple Vendor", 0, 0, []],
    98: [320, 1, False, 0, [], "EuroHiddenHouseItem", "Euro: Hidden House", 0, 0, []],
    99: [323, 1, False, 0, [], "EuroShop1Item", "Euro: Store Item 1", 0, 0, []],
    100: [323, 1, False, 0, [], "EuroShop2Item", "Euro: Store Item 2", 0, 0, []],
    101: [321, 1, False, 0, [], "EuroSlaveRoomBarrelItem", "Euro: Shrine", 0, 0, []],
    102: [314, 1, False, 0, [], "EuroAnnItem", "Euro: Ann", 0, 0, [[40, 1]]],

    103: [325, 2, False, 0, [], "", "Euro: Dark Space", 0, 0, []],

    # Mt Temple
    104: [336, 1, False, 0, [], "KressChest1Item", "Mt. Temple: Red Jewel Chest", 0, 0, []],
    105: [338, 1, False, 0, [], "KressChest2Item", "Mt. Temple: Drops Chest 1", 0, 0, []],
    106: [342, 1, False, 0, [], "KressChest3Item", "Mt. Temple: Drops Chest 2", 0, 0, []],
    107: [343, 1, False, 0, [], "KressChest4Item", "Mt. Temple: Drops Chest 3", 0, 0, []],
    108: [345, 1, False, 0, [], "KressChest5Item", "Mt. Temple: Final Chest", 0, 0, []],

    109: [332, 2, False, 0, [], "", "Mt. Temple: Dark Space 1", 0, 0, []],
    110: [337, 2, False, 0, [], "", "Mt. Temple: Dark Space 2", 0, 0, []],
    111: [343, 2, False, 0, [], "", "Mt. Temple: Dark Space 3", 0, 0, []],

    734: [338, 5, False, 0, [], "KressSkullShortcutItem", "Mt. Temple: Skull for Drops Chest 1 Shortcut", 0, 0,
          [[609, 1]]],

    # Natives'
    112: [353, 1, False, 0, [], "NativesPotItem", "Natives' Village: Statue Room", 0, 0, []],
    113: [354, 1, False, 0, [], "NativesGirlItem", "Natives' Village: Statue", 0, 0, []],

    114: [350, 2, False, 0, [], "", "Natives' Village: Dark Space", 0, 0, []],

    # Ankor Wat
    115: [361, 1, False, 0, [], "WatChest1Item", "Ankor Wat: Ramp Chest", 0, 0, []],
    116: [370, 1, False, 0, [], "WatChest2Item", "Ankor Wat: Flyover Chest", 0, 0, []],
    117: [378, 1, False, 0, [], "WatChest3Item", "Ankor Wat: U-Turn Chest", 0, 0, []],
    118: [382, 1, False, 0, [], "WatChest4Item", "Ankor Wat: Drop Down Chest", 0, 0, []],
    119: [389, 1, False, 0, [], "WatChest5Item", "Ankor Wat: Forgotten Chest", 0, 0, []],
    120: [380, 1, False, 0, [], "WatGlassesItem", "Ankor Wat: Glasses Location", 0, 0, []],
    121: [391, 1, False, 0, [], "WatSpiritItem", "Ankor Wat: Spirit", 0, 0, []],

    122: [372, 2, False, 0, [], "", "Ankor Wat: Garden Dark Space", 0, 0, []],
    123: [377, 2, False, 0, [], "", "Ankor Wat: Earthquaker Dark Space", 0, 0, []],
    124: [383, 2, False, 0, [], "", "Ankor Wat: Drop Down Dark Space", 0, 0, []],

    735: [739, 5, False, 0, [], "WatSouthScarabItem", "Ankor Wat: Scarab for Outer South Stair", 0, 0,
          [[609, 1]]],
    736: [364, 5, False, 0, [], "WatEastSliderHoleItem", "Ankor Wat: Scarab for Outer East Slider Hole", 0, 0,
          [[609, 1]]],
    738: [727, 5, False, 0, [], "WatDarkSpaceHallItem", "Ankor Wat: Skull for Inner East DS Hall", 0, 0,
          [[609, 1]]],

    # Dao
    125: [400, 1, False, 0, [], "DaoEntrance1Item", "Dao: Entrance Item 1", 0, 0, []],
    126: [400, 1, False, 0, [], "DaoEntrance2Item", "Dao: Entrance Item 2", 0, 0, []],
    127: [400, 1, False, 0, [], "DaoGrassItem", "Dao: East Grass", 0, 0, []],
    128: [403, 1, False, 0, [], "DaoSnakeGameItem", "Dao: Snake Game", 0, 0, [[609, 1]]],

    129: [400, 2, False, 0, [], "", "Dao: Dark Space", 0, 0, []],

    # Pyramid
    130: [713, 1, False, 0, [], "PyramidGaiaItem", "Pyramid: Gaia Item", 0, 0, []],
    131: [412, 1, False, 0, [], "PyramidFoyerItem", "Pyramid: Hidden Platform", 0, 0, []],
    132: [442, 1, False, 0, [], "PyramidHiero1Item", "Pyramid: Hieroglyph 1", 0, 0, []],
    133: [422, 1, False, 0, [], "PyramidRoom2ChestItem", "Pyramid: Room 2 Chest", 0, 0, []],
    134: [443, 1, False, 0, [], "PyramidHiero2Item", "Pyramid: Hieroglyph 2", 0, 0, []],
    135: [432, 1, False, 0, [], "PyramidRoom3ChestItem", "Pyramid: Room 3 Chest", 0, 0, []],
    136: [444, 1, False, 0, [], "PyramidHiero3Item", "Pyramid: Hieroglyph 3", 0, 0, []],
    137: [439, 1, False, 0, [], "PyramidRoom4ChestItem", "Pyramid: Room 4 Chest", 0, 0, []],
    138: [445, 1, False, 0, [], "PyramidHiero4Item", "Pyramid: Hieroglyph 4", 0, 0, []],
    139: [428, 1, False, 0, [], "PyramidRoom5ChestItem", "Pyramid: Room 5 Chest", 0, 0, []],
    140: [446, 1, False, 0, [], "PyramidHiero5Item", "Pyramid: Hieroglyph 5", 0, 0, []],
    141: [447, 1, False, 0, [], "PyramidHiero6Item", "Pyramid: Hieroglyph 6", 0, 0, []],

    154: [713, 2, True, 0, [61, 62, 63, 64, 65, 66], "", "Pyramid: Upper Dark Space", -1, 0, []],
    142: [413, 2, False, 0, [], "", "Pyramid: Lower Dark Space", 0, 0, []],

    739: [411, 5, False, 0, [], "PyramidEntranceOrbsItem", "Pyramid: Entrance Orbs for DS Gate", 0, 0,
          [[609, 1]]],

    # Babel
    143: [461, 1, False, 0, [], "BabelPillowItem", "Babel: Pillow", 0, 0, []],
    144: [461, 1, False, 0, [], "BabelForceFieldItem", "Babel: Force Field", 0, 0, []],

    145: [461, 2, False, 0, [], "", "Babel: Dark Space Bottom", 0, 0, []],
    146: [472, 2, False, 0, [], "", "Babel: Dark Space Top", 0, 0, []],

    # Jeweler's Mansion
    147: [715, 1, False, 0, [], "MansionChestItem", "Jeweler's Mansion: Chest", 0, 0, []],

    740: [480, 5, False, 0, [], "MansionEastGateItem", "Jeweler's Mansion: Enemy for East Gate", 0, 0,
          [[609, 1]]],
    741: [714, 5, False, 0, [], "MansionWestGateItem", "Jeweler's Mansion: Enemy for West Gate", 0, 0,
          [[609, 1]]],

    # Mystic Statues
    148: [101, 3, False, 0, [101, 102, 103, 104, 105], "", "Castoth Prize", 0, 0, []],
    # in node 101 (Gold Ship), not strictly Castoth's node
    149: [198, 3, False, 0, [100, 102, 103, 104, 105], "", "Viper Prize", 0, 0, [[609, 1]]],
    150: [244, 3, False, 0, [100, 101, 103, 104, 105], "", "Vampires Prize", 0, 0, []],
    151: [302, 3, False, 0, [100, 101, 102, 104, 105], "", "Sand Fanger Prize", 0, 0, [[609, 1]]],
    152: [448, 3, False, 0, [100, 101, 102, 103, 105], "", "Mummy Queen Prize", 0, 0, [[36, 1]]],
    153: [479, 3, False, 0, [100, 101, 102, 103, 104], "", "Babel Prize", 0, 0, []],

    # Event Switches
    500: [500, 4, True, 500, [], "", "Kara", 0, 0, []],
    501: [55, 4, True, 501, [], "", "Lilly", 0, 0, [[23, 1]]],
    502: [502, 4, True, 502, [], "", "Moon Tribe: Spirits Healed", 0, 0, []],
    503: [503, 4, True, 503, [], "", "Inca: Castoth defeated", 0, 0, []],
    504: [122, 4, True, 504, [], "", "Freejia: Found Laborer", 0, 0, []],
    505: [505, 4, True, 505, [], "", "Neil's Memory Restored", 0, 0, []],
    506: [186, 4, True, 506, [], "", "Sky Garden: Map 82 NW Switch pressed", 0, 0, [[609, 1]]],
    507: [189, 4, True, 507, [], "", "Sky Garden: Map 82 NE Switch pressed", 0, 0, []],
    508: [508, 4, True, 508, [], "", "Sky Garden: Map 82 SE Switch pressed", 0, 0, []],
    509: [509, 4, True, 509, [], "", "Sky Garden: Map 84 Statue Switch pressed", 0, 0, []],
    510: [209, 4, True, 510, [], "", "Seaside: Fountain Purified", 0, 0, [[17, 1]]],
    511: [511, 4, True, 511, [], "", "Mu: Water Lowered 1", 0, 0, []],
    512: [512, 4, True, 512, [], "", "Mu: Water Lowered 2", 0, 0, []],
    513: [274, 4, True, 513, [], "", "Angel: Puzzle Complete", 0, 0, []],
    514: [514, 4, True, 514, [], "", "Mt Kress: Drops used 1", 0, 0, []],
    515: [515, 4, True, 515, [], "", "Mt Kress: Drops used 2", 0, 0, []],
    516: [516, 4, True, 516, [], "", "Mt Kress: Drops used 3", 0, 0, []],
    517: [517, 4, True, 517, [], "", "Pyramid: Hieroglyphs placed", 0, 0, []],
    518: [518, 4, True, 518, [], "", "Babel: Castoth defeated", 0, 0, []],
    519: [519, 4, True, 519, [], "", "Babel: Viper defeated", 0, 0, []],
    520: [520, 4, True, 520, [], "", "Babel: Vampires defeated", 0, 0, []],
    521: [521, 4, True, 521, [], "", "Babel: Sand Fanger defeated", 0, 0, []],
    522: [478, 4, True, 522, [], "", "Babel: Mummy Queen defeated", 0, 0, []],
    # No weapon required because Shadow is automatic
    523: [482, 4, True, 523, [], "", "Mansion: Solid Arm defeated", 0, 0, [[609, 1]]],
    524: [89, 4, True, 524, [], "", "Inca: Diamond Block Placed", 0, 0, [[7, 1]]],
    526: [526, 4, True, 526, [], "", "Mu: Access to Hope Room 1", 0, 0, []],
    527: [527, 4, True, 527, [], "", "Mu: Access to Hope Room 2", 0, 0, []],
    528: [131, 4, True, 528, [], "", "Mine: Blocked Tunnel Open", 0, 0, [[608, 1]]],
    529: [529, 4, True, 529, [], "", "Underground Tunnel: Bridge Open", 0, 0, []],
    530: [530, 4, True, 530, [], "", "Inca: Slug Statue Broken", 0, 0, []],
    531: [531, 4, True, 531, [], "", "Mu: Beat Vampires", 0, 0, []],
    532: [198, 4, True, 532, [], "", "Sky Garden: Beat Viper", 0, 0, [[609, 1]]],
    533: [702, 4, True, 533, [], "", "Great Wall: Beat Fanger", 0, 0, [[609, 1]]],
    534: [448, 4, True, 534, [], "", "Pyramid: Beat Mummy Queen", 0, 0, [[36, 1]]],

    # Misc
    # 602: [0, 6, True, 602, [], "", "Early Firebird enabled", 0, 0, [] ],
    603: [491, 6, True, 67, [], "", "Firebird access", 0, 0, []],
    # 604: [604, 6, True, 604, [], "", "Flute", 0, 0, [] ],
    # 608: [608, 6, True, 608, [], "", "Has Any Will Ability", 0, 0, [] ],
    # 609: [609, 6, True, 609, [], "", "Has Any Attack", 0, 0, [] ],
    # 610: [610, 6, True, 610, [], "", "Has Any Ranged Attack", 0, 0)

    802: [802, 6, True, 802, [], "", "Pyramid logical access", 0, 0, []],
    803: [803, 6, True, 803, [], "", "Killer 6 logical access", 0, 0, []]
}
