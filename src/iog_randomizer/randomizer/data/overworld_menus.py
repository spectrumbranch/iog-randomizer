from typing import Final, Mapping

# Database of overworld menus
# FORMAT: { ID: (ShuffleID (0=no shuffle), Menu_ID, FromRegion, ToRegion, AssemblyLabel, ContinentName, AreaName)}
# Names are 10 characters, padded with white space (underscores).
OVERWORLD_MENUS: Final[Mapping[int, tuple[int, int, int, int, str, str, str]]] = {
    # SW Continent "\x01"
    1: (0, 1, 10, 20, "Cape", "SW Continent", "South Cape"),
    2: (0, 1, 10, 30, "Ed", "SW Continent", "Edward's__"),
    3: (0, 1, 10, 50, "Itry", "SW Continent", "Itory_____"),
    4: (0, 1, 10, 60, "Moon", "SW Continent", "Moon Tribe"),
    5: (0, 1, 10, 63, "Inca", "SW Continent", "Inca______"),

    # SE Continent "\x02"
    6: (0, 2, 11, 102, "DCst", "SE Continent", "D. Coast__"),
    7: (0, 2, 11, 110, "Frej", "SE Continent", "Freejia___"),
    8: (0, 2, 11, 133, "Mine", "SE Continent", "D. Mine___"),
    9: (0, 2, 11, 160, "Neil", "SE Continent", "Neil's____"),
    10: (0, 2, 11, 162, "Nzca", "SE Continent", "Nazca_____"),

    # NE Continent "\x03"
    11: (0, 3, 12, 250, "Angl", "NE Continent", "Angel Vil."),
    12: (0, 3, 12, 280, "Wtma", "NE Continent", "Watermia__"),
    13: (0, 3, 12, 290, "GtWl", "NE Continent", "Great Wall"),

    # N Continent "\x04"
    14: (0, 4, 13, 310, "Euro", "N Continent", "Euro______"),
    15: (0, 4, 13, 330, "Kres", "N Continent", "Mt. Temple"),
    16: (0, 4, 13, 350, "NtVl", "N Continent", "Natives'__"),
    17: (0, 4, 13, 360, "Ankr", "N Continent", "Ankor Wat_"),

    # NW Continent Overworld "\x05"
    18: (0, 5, 14, 400, "Dao", "NW Continent", "Dao_______"),
    19: (0, 5, 14, 410, "Pymd", "NW Continent", "Pyramid___")
}