from enum import IntEnum, StrEnum


class DarkRooms(IntEnum):
    ALLCURSED = -4
    MANYCURSED = -3
    SOMECURSED = -2
    FEWCURSED = -1
    NONE = 0
    FEW = 1
    SOME = 2
    MANY = 3
    ALL = 4


class Difficulty(IntEnum):
    EASY = 0
    NORMAL = 1
    HARD = 2
    EXTREME = 3


class DungeonShuffle(IntEnum):
    NONE = 0
    BASIC = 1
    CHAOS = 2
    CLUSTERED = 3


class Enemizer(IntEnum):
    NONE = 0
    LIMITED = 1
    BALANCED = 2
    FULL = 3
    INSANE = 4


class EntranceShuffle(IntEnum):
    NONE = 0
    COUPLED = 1
    UNCOUPLED = 2


class FluteOpt(IntEnum):
    START = 0
    SHUFFLE = 1
    FLUTELESS = 2


class Goal(IntEnum):
    DARK_GAIA = 0
    RED_JEWEL_HUNT = 1
    APO_GAIA = 2
    RANDOM_GAIA = 3


class Level(IntEnum):
    BEGINNER = 0
    INTERMEDIATE = 1
    ADVANCED = 2
    EXPERT = 3


class Logic(IntEnum):
    COMPLETABLE = 0
    BEATABLE = 1
    CHAOS = 2


class OrbRando(IntEnum):
    NONE = 0
    BASIC = 1
    ORBSANITY = 2


class Sprite(StrEnum):
    WILL = "will"
    BAGU = "bagu"
    INVISIBLE = "invisible"
    FREET = "freet"
    SOLAR = "solar"
    SYE = "sye"


class StartLocation(IntEnum):
    SOUTH_CAPE = 0
    SAFE = 1
    UNSAFE = 2
    FORCED_UNSAFE = 3


class StatueReq(IntEnum):
    GAME_CHOICE = 0
    PLAYER_CHOICE = 1
    RANDOM_CHOICE = 2


class PrintLevel(IntEnum):
    SILENT = -1
    ERROR = 0
    WARN = 1
    INFO = 2
    VERBOSE = 3
