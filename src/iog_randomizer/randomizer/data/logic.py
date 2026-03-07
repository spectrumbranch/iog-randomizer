from typing import Mapping, Any

# Shell logical paths for the world graph. Edges for exits etc. are added during initialization.
# IsBidirectional is only used during initialization, and is False afterward.
# Format: { ID: [0: Status(-1=restricted,0=locked,1=unlocked,2=forced_open),
#                1: StartRegion,
#                2: DestRegion,
#                3: Form flags (same as self.graph; 0 to inherit from items),
#                4: [[item1, qty1],[item2,qty2],...],
#                5: IsBidirectional
#               ] }
def get_logic(gem: list[int], goal: str, difficulty: int, dungeon_shuffle: bool, coupled_exits: bool, enemizer: str, statues_required: int, kara: int, allow_glitches: bool = False) -> Mapping[int, list[Any]]:
    # TODO: Gets mutated, Consider turning into a class [int, int, int, int, list[list[int]], bool]
    return {
        # Jeweler Rewards
        0: [0, 1, 2, 0, [[1, gem[0]]], False], # Jeweler Reward 1
        1: [0, 1, 2, 0, [[1, gem[0] - 2], [41, 1]], False],
        2: [0, 1, 2, 0, [[1, gem[0] - 3], [42, 1]], False],
        3: [0, 1, 2, 0, [[1, gem[0] - 5], [41, 1], [42, 1]], False],
        4: [0, 2, 3, 0, [[1, gem[1]]], False], # Jeweler Reward 2
        5: [0, 2, 3, 0, [[1, gem[1] - 2], [41, 1]], False],
        6: [0, 2, 3, 0, [[1, gem[1] - 3], [42, 1]], False],
        7: [0, 2, 3, 0, [[1, gem[1] - 5], [41, 1], [42, 1]], False],
        8: [0, 3, 4, 0, [[1, gem[2]]], False], # Jeweler Reward 3
        9: [0, 3, 4, 0, [[1, gem[2] - 2], [41, 1]], False],
        10: [0, 3, 4, 0, [[1, gem[2] - 3], [42, 1]], False],
        11: [0, 3, 4, 0, [[1, gem[2] - 5], [41, 1], [42, 1]], False],
        12: [0, 4, 5, 0, [[1, gem[3]]], False], # Jeweler Reward 4
        13: [0, 4, 5, 0, [[1, gem[3] - 2], [41, 1]], False],
        14: [0, 4, 5, 0, [[1, gem[3] - 3], [42, 1]], False],
        15: [0, 4, 5, 0, [[1, gem[3] - 5], [41, 1], [42, 1]], False],
        16: [0, 5, 6, 0, [[1, gem[4]]], False], # Jeweler Reward 5
        17: [0, 5, 6, 0, [[1, gem[4] - 2], [41, 1]], False],
        18: [0, 5, 6, 0, [[1, gem[4] - 3], [42, 1]], False],
        19: [0, 5, 6, 0, [[1, gem[4] - 5], [41, 1], [42, 1]], False],
        20: [0, 6, 7, 0, [[1, gem[5]]], False], # Jeweler Reward 6
        21: [0, 6, 7, 0, [[1, gem[5] - 2], [41, 1]], False],
        22: [0, 6, 7, 0, [[1, gem[5] - 3], [42, 1]], False],
        23: [0, 6, 7, 0, [[1, gem[5] - 5], [41, 1], [42, 1]], False],
        24: [0, 7, 492 if goal == "Red Jewel Hunt" else 8, 0, [[1, gem[6]]], False], # Jeweler Reward 7 (Mansion)
        25: [0, 7, 492 if goal == "Red Jewel Hunt" else 8, 0, [[1, gem[6] - 2], [41, 1]], False],
        26: [0, 7, 492 if goal == "Red Jewel Hunt" else 8, 0, [[1, gem[6] - 3], [42, 1]], False],
        27: [0, 7, 492 if goal == "Red Jewel Hunt" else 8, 0, [[1, gem[6] - 5], [41, 1], [42, 1]], False],

        # Inter-Continental Travel
        30: [0, 28, 15, 0, [[37, 1]], False], # South Cape: Erik w/ Lola's Letter
        31: [0, 102, 15, 0, [[37, 1]], False], # Coast: Turbo w/ Lola's Letter
        32: [0, 280, 15, 0, [[37, 1]], False], # Watermia: Bridgeman w/ Lola's Letter
        33: [0, 160, 161, 0, [[13, 1], [611, 1]], False], # Neil's: Neil w/ Memory Melody
        34: [0, 314, 17, 0, [[505, 1]], False], # Euro: Neil w/ Memory restored
        35: [0, 402, 17, 0, [[505, 1]], False], # Dao: Neil w/ Memory restored
        36: [0, 60, 64, 0, [[25, 1]], False], # Moon Tribe healed w/ Teapot
        37: [0, 170, 16, 0, [[502, 1]], False], # Sky Garden: Spirits w/ spirits healed
        38: [0, 280, 288, 0, [[24, 1]], False], # Watermia: Stablemaster w/ Will
        39: [0, 310, 311, 0, [[24, 1]], False], # Euro: Stablemaster w/ Will
        40: [0, 350, 351, 0, [[10, 1]], False], # Natives': Child Guide w/ Large Roast

        # Edward's / Tunnel
        60: [0, 32, 33, 0, [[2, 1]], True], # Escape/Enter cell w/Prison Key
        59: [0, 38, 42, 0, [[608, 1]], True], # Pass statues with a Will ability
        61: [0, 38, 42, 0, [[612, 1]], True], # Pass statues with telekinesis
        62: [0, 42, 39, 0, [[609, 1]], False], # Pass spike balls to chest with any attack
        703: [0, 47, 720, 0, [[704, 1]], True], # Worm orb opens Dark Space
        63: [0, 47, 529, 0x06, [], False], # Open bridge via F/S
        64: [0, 47, 704, 0, [[529, 1]], True], # Traverse bridge to 2nd area
        704: [0, 704, 705, 0, [[705, 1]], True], # Skeleton barrier between 2nd and 3rd areas
        705: [0, 705, 706, 0, [[706, 1]], True], # Skeleton barrier between 3rd and final areas

        # Itory
        70: [0, 50, 51, 0, [[9, 1], [611, 1]], False], # Town appears w/ Lola's Melody

        # Moon Tribe
        80: [0, 61, 62, 0, [[608, 1]], False], # Cave challenge w/ Will ability
        600: [0, 61, 62 if allow_glitches else 61, 0, [[604, 1]], False],
        # Cave challenge itemless w/ glitches and flute

        # Inca / Gold Ship / Freejia
        88: [0, 99, 75 if coupled_exits else 99, 0, [], False],
        # Materialize Z-ladder door coupling if applicable
        89: [0, 72, 99 if enemizer == "None" and allow_glitches else 72, 0, [], False],
        # Map 29 progression w/ Z-ladder glitch
        706: [0, 72, 70, 0, [[709, 1], [801, 1]], True],
        # Inca exterior (29) N<->NE via 4-Way orb, ignored during dungeon construction
        707: [0, 74, 72, 0, [[707, 1], [801, 1]], True],
        # Inca exterior (29) SW<->N via 4-Way orb, ignored during dungeon construction
        708: [0, 75, 72, 0, [[708, 1], [801, 1]], True],
        # Inca exterior (29) SE<->N via 4-Way orb, ignored during dungeon construction
        700: [0, 73, 700, 0, [[64, 1], [54, 2]], False], # Inca west 4-Way orb from C with upgraded Friar
        90: [0, 77, 78, 0, [[3, 1], [4, 1]], False], # Map 30 to Castoth w/ Inca Statues
        91: [0, 80, 530, 0, [[608, 1]], False], # Break blocking slug statue w/ Will ability
        92: [0, 81, 530, 0, [[608, 1]], False], # Break blocking slug statue w/ Will ability
        93: [0, 80, 81, 0, [[530, 1]], True], # Passage after blocking slug statue is broken
        710: [0, 82, 83, 0, [[710, 1]], False], # Inca N/S ramp (33) via whirligig orb
        94: [0, 85, 707, 0x06, [], False], # Map 35 get orb w/ F/S
        95: [0, 85, 707, 0, [[610, 1]], False], # Map 35 get orb w/ ranged
        709: [0, 85, 86, 0, [[711, 1]], False], # Inca E/W ramp (35) via whirligig orb
        97: [0, 91, 92, 0, [[608, 1]], False], # Map 38 break statues w/ Will ability
        711: [0, 96, 95, 0, [[713, 1]], False], # Map 40 reverse via 4-Way orb
        98: [0, 95, 96, 0, [[609, 1]], False], # DS spike hall requires an attack to pass the 4-Way
        99: [0, 97, 503, 0x06, [], False], # Castoth as F/S
        100: [0, 97, 503, 0, [[604, 1]], False], # Castoth with Flute
        101: [0,  97,  98,     0, [[503, 1]], False],  # Pass Castoth (the 97-98 exit is not in exits)

        # Diamond Mine
        712: [0, 130, 708, 0, [[715, 1]], True], # Map 61 S fence progression via monster
        713: [0, 708, 709, 0, [[714, 1]], True], # Map 61 C fence progression via monster
        714: [0, 709, 131, 0, [[716, 1]], True], # Map 61 N fence progression via monster
        702: [0, 709, 701, 0, [[610, 1]], False], # Map 61 C lizard from N via ranged
        715: [0, 136, 721, 0, [[718, 1]], True], # Map 64 appearing DS via worm orb
        117: [0, 138, 139, 0, [[63, 1]], False], # Map 65 ramp access via Spin Dash
        716: [0, 138, 139, 0, [[719, 1]], False], # Map 65 ramp access via worm orb
        118: [0, 138, 710, 0, [[610, 1]], False], # Map 65 worm access via ranged

        # Sky Garden
        130: [0, 170, 171, 0, [[14, 4]], False], # Boss access w/ Crystal Balls
        131: [0, 177, 711, 0, [[610, 1]], False], # SE Top (79) robot orb via ranged
        718: [0, 177, 178, 0, [[720, 1]], True], # SE Top (79) barrier via robot orb
        720: [0, 180, 716, 0, [[721, 1]], True], # SE Bot (80) chest via robot orb
        721: [0, 181, 168, 0, [[722, 1]], True], # SW Top (81) C<->N via robot orb
        723: [0, 181, 182, 0, [[724, 1]], True], # SW Top (81) C<->W via worm orb
        133: [0, 168, 182, 0, [[506, 1]], True], # SW Top progression w/ switch 1
        134: [0, 182, 183, 0, [[507, 1]], True], # SW Top progression w/ switch 2
        135: [0, 182, 184, 0, [[608, 1]], True], # SW Top SW->SE, break statues w/ Will ability
        138: [0, 184, 185, 0, [[508, 1], [608, 1]], False], # SW Top ramp chest w/ switch 3 & Will ability
        141: [0, 181, 182, 0, [[63, 1]], False], # SW Top (81) ramps w/ Spin Dash
        142: [0, 181, 184, 0, [[63, 1]], False], # SW Top (81) ramps w/ Spin Dash
        143: [0, 182, 185, 0, [[63, 1]], False], # SW Top (81) ramps w/ Spin Dash
        601: [0, 181, 182 if allow_glitches else 181, 0x01, [], False],
        # SW Top (81) C->SW via ramp glitch jump
        603: [0, 182, 185 if allow_glitches else 182, 0x01, [], False],
        # SW Top (81) SW->chest via ramp glitch jump
        739: [0, 187, 508, 0, [[725, 1], [609, 1], [612, 1]], False],
        # SW Bot (82) switch via fire cage orb, attack, and telekinesis
        144: [0, 188, 189, 0x06, [], False], # SW Bot (82) cage switch w/ reach
        145: [0, 188, 189 if allow_glitches else 188, 0, [[604, 1]], False],
        # SW Bot (82) cage switch w/ Glitches + Flute
        146: [0, 192, 190, 0, [[63, 1]], False], # NW Top (83) backward w/ Spin Dash
        148: [0, 195, 509, 0, [[610, 1], [612, 1]], False], # NW Bot (84) statue w/ ranged and telekinesis
        149: [0, 195, 509, 0, [[65, 1], [612, 1]], False], # NW Bot (84) statue w/ Aura Barrier and telekinesis
        150: [0, 195, 197, 0, [[509, 1]], True], # NW Bot (84) traversal with statue switch
        152: [0, 170, 16, 0, [[502, 1]], False], # Moon Tribe passage w/ spirits healed
        153: [0, 198, 199,     0, [[532, 1]], False], # Pass Viper

        # Mu
        724: [0, 212, 722, 0, [[726, 1]], True], # Mu entrance (95) gate via golem orb
        171: [0, 212, 213, 0, [[511, 1]], True], # Map 95 top-midE w/ water lowered 1
        172: [0, 213, 215, 0, [[512, 1]], True], # Map 95 midE-botE w/ water lowered 2
        173: [0, 214, 216, 0, [[512, 1]], True], # Map 95 midw-botW w/ water lowered 2
        174: [0, 217, 218, 0, [[511, 1]], True], # Map 96 top-mid w/ water lowered 1
        726: [0, 217, 725, 0, [[727, 1]], True], # Mu NE (96) N/S semiprogression via rocks
        727: [0, 723, 725, 0, [[728, 1]], True], # Mu NE (96) N/S semiprogression via rocks
        753: [0, 723, 726, 0, [[610, 1]], False], # Mu NE, N orb from S, via ranged
        754: [0, 217, 724, 0, [[610, 1]], False], # Mu NE, S orb from N, via ranged
        175: [0, 222, 221, 0, [[511, 1], [610, 1]], False], # Map 97 midN->island w/ water lowered 1 & ranged
        176: [0, 222, 221 if allow_glitches else 222, 0, [[511, 1]], False],
        # Map 97 midN->island w/ water lowered 1 & glitches
        178: [0, 226, 227, 0, [[511, 1]], True], # Map 98 top-midE w/ water lowered 1
        179: [0, 227, 229, 0, [[512, 1]], True], # Map 98 midE-botE w/ water lowered 2
        180: [0, 228, 230, 0, [[512, 1]], True], # Map 98 midW-botW w/ water lowered 2
        181: [0, 229, 230, 0, [[62, 1], [512, 1]], True], # Map 98 W/E Slider hole
        182: [0, 233, 245, 0, [[609, 1]], True], # SW MidE spike buttons require an attack
        184: [0, 237, 238, 0, [[62, 1], [511, 1]], True], # Map 101 midW-midE w/ Psycho Slider
        185: [0, 240, 241, 0, [[19, 2]], False], # Map 102 progression w/ Rama Statues
        186: [0, 526, 511, 0, [[18, 1]], False], # Water lowered 1 w/ Hope Statue
        187: [0, 527, 511, 0, [[18, 1]], False], # Water lowered 1 w/ Hope Statue
        188: [0, 526, 512, 0, [[18, 2], [527, 1], [511, 1]], False],
        # Water lowered 2 w/ Hope Statues, both rooms, and water lowered 1
        189: [0, 527, 512, 0, [[18, 2], [526, 1], [511, 1]], False],
        # Water lowered 2 w/ Hope Statues, both rooms, and water lowered 1
        190: [0, 244, 531, 0x6, [], False], # Vampires as F/S
        191: [0, 244, 531,  0, [[604 if difficulty < 3 else 609, 1]], False], # Vampires with Flute, or any attack if playing Extreme
        192: [0, 244, 242,  0, [[531, 1]], False], # Pass Vampires (the 244-242 exit is not in exits)

        # Angel Dungeon
        214: [0, 272, 273, 0, [[513, 1]], False], # Ishtar's chest w/ puzzle complete
        215: [0, 261, 278, 0, [[609, 1]], True], # Passing a Draco requires an attack
        216: [0, 263, 279, 0, [[609, 1]], True], # Passing a Draco requires an attack

        # Great Wall
        218: [0, 292, 293, 0, [[609, 1]], False], # Drop room forward requires an attack for the button
        219: [0, 293, 291, 0, [[63, 1]], True], # Map 131 (drop room) backwards w/ Spin Dash
        220: [0, 294, 295 if allow_glitches else 294, 0, [[604, 1]], False], # Map 133 W->C w/ glitches and Flute
        221: [0, 296, 295, 0, [[63, 1]], False], # Map 133 E->C w/ Spin Dash
        222: [0, 296, 295, 0x06, [], False], # Map 133 E->C w/ Freedan or Shadow
        223: [0, 296, 294, 0, [[63, 1]], False], # Map 133 C->W w/ Spin Dash
        728: [0, 298, 299, 0, [[732, 1]], True], # Map 135 progression w/ archer orb
        227: [0, 298, 712, 0, [[610, 1]], False], # Map 135 archer via ranged
        228: [0, 299, 712, 0, [[610, 1]], False], # Map 135 archer via ranged
        229: [0, 300, 301, 0, [[63, 1]], True], # Map 136 progression w/ Spin Dash
        230: [0, 702, 303,     0, [[533, 1]], False], # Pass Fanger

        # Mt. Temple
        240: [0, 331, 332, 0, [[63, 1]], True], # Map 161 progression w/ Spin Dash
        242: [0, 333, 514, 0, [[26, 1 if not dungeon_shuffle else 3]], False], # Use Mushroom drops 1
        750: [0, 333, 335, 0, [[514, 1]], True], # Drops vine 1
        244: [0, 339, 515, 0, [[26, 2 if not dungeon_shuffle else 3]], False], # Use Mushroom drops 2
        751: [0, 339, 340, 0, [[515, 1]], True], # Drops vine 2
        246: [0, 340, 516, 0, [[26, 3]], False], # Use Mushroom drops 3
        752: [0, 340, 341, 0, [[516, 1]], True], # Drops vine 3

        # Natives'
        250: [0, 353, 354, 0, [[29, 1]], False], # Statues awake w/ Gorgon Flower

        # Ankor Wat
        260: [0, 361, 739, 0, [[64, 1], [54, 2]], False], # Map 177 orb w/ upgraded Friar
        729: [0, 361, 362, 0, [[735, 1], [801, 1]], True],
        # Wat Outer South (177) via scarab orb, ignored during dungeon construction
        261: [0, 363, 364, 0, [[63, 1]], False], # Map 178 S->C w/ Spin Dash
        262: [0, 364, 365, 0, [[62, 1], [736, 1]], False], # Map 178 C->N w/ Psycho Slider and scarab key
        263: [0, 365, 364, 0, [[62, 1]], False], # Map 178 N->C w/ Psycho Slider
        264: [0, 367, 366, 0, [[63, 1]], False], # Map 179 W->E w/ Spin Dash
        265: [0, 369, 370, 0, [[62, 1]], False], # Map 181 N->C w/ Psycho Slider
        266: [0, 370, 371, 0, [[63, 1]], False], # Map 181 C->S w/ Spin Dash
        267: [0, 373, 374, 0, [[66, 1]], False], # Map 183 S->NW w/ Earthquaker
        268: [0, 373, 374, 0, [[64, 1], [54, 2]], False], # Map 183 S->NW w/ upgraded Friar
        269: [0, 373, 374 if allow_glitches else 373, 0, [[64, 1]], False],
        # Map 183 S->NW w/ Friar and glitches
        271: [0, 376, 727, 0, [[64, 1]], False], # Map 184 orb access via Friar
        272: [0, 376, 727, 0, [[36, 1]], False], # Map 184 orb access via Shadow
        731: [0, 376, 377, 0, [[738, 1]], True], # Map 184 S<->N w/ skull orb
        273: [0, 384, 385 if allow_glitches else 384, 0, [[62, 1]], True],
        # Map 188 S-N w/ Slider and glitches
        274: [0, 384, 385, 0, [[62, 1], [28, 1]], True], # Map 188 S-N w/ Slider and Glasses
        275: [0, 386, 387, 0, [[62, 1]], True], # Map 189 S-N w/ Slider

        # Pyramid
        290: [0, 410, 411, 0, [[62, 1]], True], # Map 204 pass orbs w/ Slider
        291: [0, 410, 411, 0, [[63, 1]], True], # Map 204 pass orbs w/ Spin
        292: [0, 410, 411 if allow_glitches else 410, 0, [], True], # Map 204 pass orbs w/ "glitches"
        736: [0, 411, 713, 0, [[739, 1]], False], # Map 204 top DS w/ orb orb
        293: [0, 713, 412, 0, [[36, 1], [739, 1]], False], # Map 204 progression w/ Aura and DS orb
        294: [0, 713, 413, 0, [[36, 1], [739, 1]], False], # Map 204 progression w/ Aura and DS orb
        295: [0, 415, 449, 0, [[30, 1], [31, 1], [32, 1], [33, 1], [34, 1], [35, 1], [38, 1]], False],
        # Boss w/ Hieros+Journal
        296: [0, 416, 417, 0, [[63, 1]], True], # Map 206 progression w/ Spin Dash
        298: [0, 418, 419, 0, [[63, 1]], True], # Map 207 progression w/ Spin Dash
        300: [0, 426, 427, 0, [[36, 1]], False], # Map 212 progression w/ Aura
        301: [0, 426, 427, 0, [[66, 1]], False], # Map 212 progression w/ Earthquaker
        302: [0, 427, 428, 0, [[36, 1]], False], # Map 212 to SE chest w/ Aura
        303: [0, 427, 429, 0, [[36, 1]], False], # Map 212 progression w/ Aura
        304: [0, 427, 429, 0, [[66, 1]], False], # Map 212 progression w/ Earthquaker
        305: [0, 431, 432, 0, [[63, 1]], True], # Map 214 to NE chest w/ Spin Dash
        306: [0, 431, 434, 0, [[36, 1]], False], # Map 214 progression w/ Aura
        307: [0, 431, 433, 0, [[64, 1]], False], # Map 214 progression w/ Friar
        308: [0, 438, 439, 0, [[63, 1]], True], # Map 217 progression w/ Spin Dash
        310: [0, 440, 441, 0, [[63, 1]], True], # Map 219 progression w/ Spin Dash
        309: [0, 435, 450,    0, [[803, 1], [63, 1]], True], # Killer 6 w/ logical access and Spin Dash (so Will can pass in dungeon shuffle)
        312: [0, 435, 450,    0, [[803, 1], [36, 1]], True], # Killer 6 w/ logical access and Aura
        313: [0, 435, 450,    0, [[803, 1], [64, 1], [54, 1]], True], # Killer 6 w/ logical access and upgraded Friar
        314: [0, 411, 414, 0, [[517, 1]], False], # Pyramid to boss w/hieroglyphs placed
        315: [0, 448, 451,    0, [[534, 1]], False], # Pass Mummy Queen

        # Babel / Mansion items 740,741
        320: [0, 461, 462, 0x0f, [[36, 1], [39, 1]], False], # Map 223 w/ Aura and Ring, any form
        321: [0, 473, 479, 0, [[522, 1]], False], # Olman statue w/ Mummy Queen 2
        732: [0, 480, 714, 0, [[740, 1]], True], # Mansion east gate with monster orb
        734: [0, 714, 715, 0, [[741, 1]], True], # Mansion west gate with monster orb
        323: [0, 715, 481, 0, [[62, 1]], True], # Mansion progression w/ Slider
        # Solid Arm always warps to top of Babel, but only Extreme difficulty has edges to include SA;
        # this prevents lower difficulties from requiring SA for either the statue or a continent warp.
        324: [0, 482, 482 if difficulty < 3 else 472, 0, [[523, 1]], False], # Warp
        322: [0, 473, 473 if difficulty < 3 else 479, 0, [[523, 1]], False], # Statue

        # Endgame / Misc
        400: [0, [49, 150, 270, 345, 391][kara - 1], 490, 0, [[20, 1]], False], # Rescue Kara w/ Magic Dust
        405: [0, 490, 491, 0x0f, [[36, 1], [39, 1], [602, 1]], False],
        # (Early) Firebird w/ Kara, Aura, Ring, and the setting
        406: [0, 490, 492, 0x0f, [[36, 1], [100, 0], [101, 0], [102, 0], [103, 0], [104, 0], [105, 0]], False],
        # Beat Game w/Statues and Aura
        407: [0, 490, 492, 0x0f, [[36, 1], [106, statues_required]], False],
        # Beat Game w/Statues and Aura (player choice)
        # RJH: link goal to inaccessible Mansion entrance for completability
        408: [0, 492, 8 if goal == "Red Jewel Hunt" else 492, 0, [], False]
    }
