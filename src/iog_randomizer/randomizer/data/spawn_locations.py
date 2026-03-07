from typing import Mapping

# Dark Space info required for random start.
# ID is shared with the DS's entry in item_locations (or -1 for School).
# Format: { ID: (0: Safety type,
#                1: Map ID outside DS,
#                2: DS index in-game,
#                3: Allow txform/F abilities (bool)
#               ) }
def get_spawn_locations(entrance_shuffle: bool, dungeon_shuffle: bool, difficulty: int, flute: str) -> Mapping[int, tuple[str, int, int, int]]:
    return {
        -1: ("", 0x08, 0x00, 0),  # School
        10: ("Safe", 0x01, 0x00, 0),  # Cape exterior
        14: ("Unsafe" if entrance_shuffle else "", 0x0b, 0x01, 0),  # Prison
        19: ("Unsafe", 0x12, 0x02, 1),  # EdDg final
        22: ("Safe", 0x15, 0x03, 0),  # Itory
        29: ("Unsafe", 0x28, 0x04, 1),  # Inca near melody
        30: ("Unsafe", 0x26, 0x05, 1),  # Inca slug DS
        31: ("", 0x1e, 0x06, 1),  # Inca Castoth
        39: ("Safe", 0x34, 0x07, 0),  # Freejia
        46: ("Unsafe", 0x40, 0x08, 1),  # Mine hidden
        47: ("Unsafe", 0x3d, 0x09, 1),  # Mine near false wall
        48: ("Unsafe" if dungeon_shuffle else "", 0x42, 0x0a, 1),  # Mine behind false wall
        57: ("Safe", 0x4c, 0x0b, 0),  # SkGn foyer
        58: ("Unsafe", 0x56, 0x0c, 1),  # SkGn blue room
        59: ("", 0x51, 0x0d, 1),  # SkGn inside fence
        60: ("Unsafe", 0x54, 0x0e, 1),  # SkGn NW dark side
        66: ("Safe", 0x5a, 0x0f, 0),  # SeaPal
        74: ("", 0x60, 0x10, 1),  # Mu NE
        75: ("", 0x62, 0x11, 1),  # Mu W
        77: ("Safe", 0x6c, 0x12, 0),  # Angl
        88: ("Safe", 0x7c, 0x13, 0),  # Wtrm
        93: ("Unsafe", 0x85, 0x14, 1),  # GtWl 1
        94: ("Unsafe", 0x86, 0x15, 1),  # GtWl Spin Dash
        95: ("", 0x88, 0x16, 1),  # GtWl final
        103: ("Safe", 0x99, 0x17, 0),  # Euro
        109: ("Unsafe", 0xa1, 0x18, 1),  # Kress 1
        110: ("Unsafe", 0xa3, 0x19, 1),  # Kress 2
        111: ("", 0xa7, 0x1a, 1),  # Kress 3
        114: ("Safe", 0xac, 0x1b, 0),  # NtVl
        122: ("Unsafe", 0xb6, 0x1c, 1),  # Ankr Garden
        123: ("", 0xb8, 0x1d, 1),  # Ankr inner east
        124: ("Unsafe", 0xbb, 0x1e, 1),  # Ankr dropdown
        129: ("Safe", 0xc3, 0x1f, 0),  # Dao
        154: ("",       0xcc, 0x20, 1),  # Pymd upper
        142: ("Unsafe", 0xcc, 0x21, 1),  # Pymd lower
        145: ("Forced Unsafe" if difficulty == 3 and flute == "Start" else "", 0xdf, 0x22, 0),
        # Babel lower
        146: ("Safe", 0xe3, 0x23, 0)  # Babel upper
    }