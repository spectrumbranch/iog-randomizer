from typing import Final, Mapping

# Database of enemy types
# FORMAT: { ID: (0: Enemyset ID,
#                1: ASM define for addr,
#                2: Default stat block,
#                3: Type(1=stationary,2=walking,3=flying),
#                4: OnWalkableTile,
#                5: CanBeRandom,
#                6: Name
#               ) }
ENEMIES: Final[Mapping[int, tuple[int, str, int, int, bool, bool, str]]] = {
    # Underground Tunnel
    0: (0, "EnemizerBatAddr", 0x05, 2, True, True, "Bat"),  # a8755
    1: (0, "EnemizerRibberAddr", 0x01, 2, True, True, "Ribber"),
    2: (0, "EnemizerCanalWormAddr", 0x02, 1, False, True, "Canal Worm"),
    3: (0, "EnemizerKingBatAddr", 0x03, 2, True, False, "King Bat"),
    4: (0, "EnemizerSkullChaserAddr", 0x10, 2, True, True, "Skull Chaser"),
    5: (0, "EnemizerBatMinion1Addr", 0x04, 2, True, False, "Bat Minion 1"),
    6: (0, "EnemizerBatMinion2Addr", 0x04, 2, True, False, "Bat Minion 2"),
    7: (0, "EnemizerBatMinion3Addr", 0x04, 2, True, False, "Bat Minion 3"),
    8: (0, "EnemizerBatMinion4Addr", 0x04, 2, True, False, "Bat Minion 4"),

    # Inca Ruins
    10: (1, "EnemizerSluggerAddr", 0x0b, 2, True, True, "Slugger"),
    11: (1, "EnemizerScuttlebugAddr", 0x0b, 2, True, False, "Scuttlebug"),
    12: (1, "EnemizerMudpitAddr", 0x0a, 2, True, True, "Mudpit"),
    13: (1, "EnemizerFourWayAddr", 0x0c, 1, True, True, "Four Way"),
    14: (2, "EnemizerSplopAddr", 0x0f, 2, True, True, "Splop"),
    15: (2, "EnemizerWhirligigAddr", 0x0e, 3, False, True, "Whirligig"),
    16: (2, "EnemizerStoneLordRAddr", 0x0d, 2, True, False, "Stone Lord R"),  # shoots fire
    17: (2, "EnemizerStoneLordDAddr", 0x0d, 2, True, True, "Stone Lord D"),  # shoots fire
    18: (2, "EnemizerStoneLordUAddr", 0x0d, 2, True, False, "Stone Lord U"),  # shoots fire
    19: (2, "EnemizerStoneLordLAddr", 0x0d, 2, True, False, "Stone Lord L"),  # shoots fire
    20: (2, "EnemizerStoneGuardRAddr", 0x0d, 2, True, False, "Stone Guard R"),  # throws spears
    21: (2, "EnemizerStoneGuardLAddr", 0x0d, 2, True, False, "Stone Guard L"),  # throws spears
    22: (2, "EnemizerStoneGuardDAddr", 0x0d, 2, True, True, "Stone Guard D"),  # throws spears
    23: (2, "EnemizerWhirligigStationaryAddr", 0x0e, 1, False, False, "Whirligig (stationary)"),

    # Diamond Mine
    30: (3, "EnemizerFlayzer1Addr", 0x18, 2, True, True, "Flayzer 1"),
    31: (3, "EnemizerFlayzer2Addr", 0x18, 2, True, False, "Flayzer 2"),
    32: (3, "EnemizerFlayzer3Addr", 0x18, 2, True, False, "Flayzer 3"),
    33: (3, "EnemizerEyeStalker1Addr", 0x19, 2, True, True, "Eye Stalker"),
    34: (3, "EnemizerEyeStalkerstoneAddr", 0x19, 2, True, False, "Eye Stalker (stone)"),
    35: (3, "EnemizerGrunditAddr", 0x1a, 1, True, True, "Grundit"),
    #            36: (3,"\xf5\xa4\x8a",0x1a,"Grundit (stationary)"),  # Can't randomize this guy

    # Sky Garden
    40: (4, "EnemizerBlueCyberAddr", 0x1d, 2, True, True, "Blue Cyber"),
    41: (4, "EnemizerDynapede1Addr", 0x1b, 2, True, True, "Dynapede 1"),
    42: (4, "EnemizerDynapede2Addr", 0x1b, 2, True, False, "Dynapede 2"),
    43: (5, "EnemizerRedCyberAddr", 0x1e, 2, True, True, "Red Cyber"),
    44: (5, "EnemizerNitropedeAddr", 0x1c, 2, True, True, "Nitropede"),

    # Mu
    50: (6, "EnemizerSlipperAddr", 0x2b, 2, True, True, "Slipper"),
    51: (6, "EnemizerSkuddleAddr", 0x2a, 2, True, True, "Skuddle"),
    52: (6, "EnemizerCyclopsAddr", 0x28, 2, True, True, "Cyclops"),
    53: (6, "EnemizerFlasherAddr", 0x29, 3, True, True, "Flasher"),
    54: (6, "EnemizerCyclopsAsleepAddr", 0x28, 2, True, False, "Cyclops (asleep)"),
    55: (6, "EnemizerSlipperFallingAddr", 0x2b, 2, True, True, "Slipper (falling)"),

    # Angel Dungeon
    60: (7, "EnemizerDiveBatAddr", 0x2d, 3, False, True, "Dive Bat"),
    61: (7, "EnemizerSteelbonesAddr", 0x2c, 2, True, True, "Steelbones"),
    62: (7, "EnemizerDracoAddr", 0x2e, 1, True, True, "Draco"),
    63: (7, "EnemizerRamskullAddr", 0x2e, 1, True, True, "Ramskull"),

    # Great Wall
    70: (8, "EnemizerArcher1Addr", 0x33, 2, True, True, "Archer 1"),
    71: (8, "EnemizerArcherStatueAddr", 0x33, 2, True, False, "Archer Statue"),
    72: (8, "EnemizerEyesoreAddr", 0x34, 2, True, True, "Eyesore"),
    73: (8, "EnemizerFireBug1Addr", 0x35, 3, False, True, "Fire Bug 1"),
    74: (8, "EnemizerFireBug2Addr", 0x33, 3, False, False, "Fire Bug 2"),
    75: (8, "EnemizerAspAddr", 0x32, 2, True, True, "Asp"),
    76: (8, "EnemizerArcher2Addr", 0x33, 2, True, False, "Archer 2"),
    77: (8, "EnemizerArcher3Addr", 0x33, 2, True, False, "Archer 3"),
    78: (8, "EnemizerArcherStatueSwitch1Addr", 0x46, 2, True, False, "Archer Statue (switch) 1"),
    79: (8, "EnemizerArcherStatueSwitch2Addr", 0x33, 2, True, False, "Archer Statue (switch) 2"),

    # Mt. Kress
    80: (9, "EnemizerSkulkerNSAddr", 0x3e, 3, True, True, "Skulker (N/S)"),
    81: (9, "EnemizerSkulkerEW1Addr", 0x3e, 3, True, True, "Skulker (E/W) 1"),
    82: (9, "EnemizerSkulkerEW2Addr", 0x3e, 3, True, False, "Skulker (E/W) 2"),
    83: (9, "EnemizerSkulkerEW3Addr", 0x3e, 3, True, False, "Skulker (E/W) 3"),
    84: (9, "EnemizerYorrickEW1Addr", 0x3d, 3, False, True, "Yorrick (E/W) 1"),
    85: (9, "EnemizerYorrickEW2Addr", 0x3d, 3, False, False, "Yorrick (E/W) 2"),
    86: (9, "EnemizerYorrickNS1Addr", 0x3d, 3, False, True, "Yorrick (N/S) 1"),
    87: (9, "EnemizerYorrickNS2Addr", 0x3d, 3, False, False, "Yorrick (N/S) 2"),
    88: (9, "EnemizerFireSpriteAddr", 0x3f, 3, False, True, "Fire Sprite"),
    89: (9, "EnemizerAcidSplasherAddr", 0x3c, 2, True, True, "Acid Splasher"),
    90: (9, "EnemizerAcidSplasherStationaryEAddr", 0x3c, 2, True, False, "Acid Splasher (stationary E)"),
    91: (9, "EnemizerAcidSplasherStationaryWAddr", 0x3c, 2, True, False, "Acid Splasher (stationary W)"),
    92: (9, "EnemizerAcidSplasherStationarySAddr", 0x3c, 2, True, False, "Acid Splasher (stationary S)"),
    93: (9, "EnemizerAcidSplasherStationaryNAddr", 0x3c, 2, True, False, "Acid Splasher (stationary N)"),

    # Ankor Wat
    100: (10, "EnemizerShrubberAddr", 0x49, 2, True, True, "Shrubber"),
    101: (10, "EnemizerShrubber2Addr", 0x49, 2, True, False, "Shrubber 2"),
    102: (10, "EnemizerZombieAddr", 0x46, 2, True, True, "Zombie"),
    103: (10, "EnemizerZipFlyAddr", 0x4a, 3, True, True, "Zip Fly"),  # False for now...
    104: (11, "EnemizerGoldcapAddr", 0x42, 3, True, True, "Goldcap"),  # i.e. flying skull
    105: (11, "EnemizerGorgonAddr", 0x45, 2, True, True, "Gorgon"),
    106: (11, "EnemizerGorgonDropperAddr", 0x45, 2, True, False, "Gorgon Dropper"),
    107: (11, "EnemizerFrenzie1Addr", 0x43, 2, True, False, "Frenzie 1"),  # i.e. wall skull stationary
    108: (11, "EnemizerFrenzie2Addr", 0x43, 2, True, True, "Frenzie 2"),  # i.e. wall skull moving
    109: (11, "EnemizerWatScarab1Addr", 0x44, 1, False, True, "Wall Walker 1"),
    110: (11, "EnemizerWatScarab2Addr", 0x3a, 1, False, False, "Wall Walker 2"),
    111: (11, "EnemizerWatScarab3Addr", 0x44, 1, False, False, "Wall Walker 3"),
    112: (11, "EnemizerWatScarab4Addr", 0x3a, 1, False, False, "Wall Walker 4"),
    113: (11, "EnemizerGorgonBlockAddr", 0x45, 2, True, False, "Gorgon (block)"),

    # Pyramid
    120: (12, "EnemizerMysticBallStationaryAddr", 0x4f, 1, True, True, "Mystic Ball (stationary)"),
    121: (12, "EnemizerMysticBall1Addr", 0x4f, 2, True, True, "Mystic Ball 1"),
    122: (12, "EnemizerMysticBall2Addr", 0x4f, 2, True, True, "Mystic Ball 2"),
    123: (12, "EnemizerTutsAddr", 0x4e, 2, True, True, "Tuts"),  # i.e. spearman
    124: (12, "EnemizerBlasterAddr", 0x51, 1, True, True, "Blaster"),  # i.e. bird head
    125: (12, "EnemizerHauntStationaryAddr", 0x4c, 2, True, False, "Haunt (stationary)"),  # i.e. wall mummy
    126: (12, "EnemizerHauntAddr", 0x4c, 2, True, True, "Haunt"),  # i.e. loose mummy

    # Babel Tower
    #            130: (14,"\xd7\x99\x8a",0x5a,"Castoth (boss)"),
    #            131: (14,"\xd5\xd0\x8a",0x5b,"Viper (boss)"),
    #            132: (14,"\x50\xf1\x8a",0x5c,"Vampire (boss)"),
    #            133: (14,"\x9c\xf1\x8a",0x5c,"Vampire (boss)"),
    #            134: (14,"\x00\x80\x8",0x5d,"Sand Fanger (boss)"),
    #            135: (14,"\x1a\xa6\x8",0x5e,"Mummy Queen (boss)"),

    # Jeweler's Mansion
    140: (13, "EnemizerFlayzerAddr", 0x61, 2, True, True, "Mansion Flayzer"),
    141: (13, "EnemizerGrunditAddr", 0x63, 1, True, True, "Mansion Grundit"),
    142: (13, "EnemizerEyeStalker2Addr", 0x62, 2, True, False, "Mansion Eye Stalker 2"),
    143: (13, "EnemizerEyeStalker1Addr", 0x62, 2, True, True, "Mansion Eye Stalker 1")
    # Bosses
    #            24: (15,"\x03\x9b\x8a",0x14,"Castoth (boss)"),
    #            45: (15,"\x6f\xd1\x8a",0x27,"Viper (boss)"),
    #            55: (15,"\xf7\xf1\x8a",0x2f,"Vampire (boss)"),
    #            56: (15,"\xc8\xf3\x8a",0x30,"Vampire (boss)"),
    #            79: (15,"\x5c\x81\x8",0x36,"Sand Fanger (boss)"),
    #            128: (15,"\xb6\xa6\x8",0x50,"Mummy Queen (boss)"),
    #            143: (15,"\x09\xf7\x88",0x5f,"Solid Arm (boss)"),
    #            140: (15,"\xaa\xee\x8c",0x54,"Dark Gaia"]
}