from typing import Final, Mapping

# Database of enemy groups and spritesets
# FORMAT: { ID: [Header card define name, Friendly name]}
ENEMY_SETS: Final[Mapping[int, list[str]]] = {
    0: ["CardMonstersEdDg", "Underground Tunnel"],
    1: ["CardMonstersIncaSpinners", "Inca Ruins (Mud Monster and Larva)"],
    2: ["CardMonstersIncaStatues", "Inca Ruins (Statues)"],
    3: ["CardMonstersMine", "Diamond Mine"],
    4: ["CardMonstersSkGnTop", "Sky Garden (top)"],
    5: ["CardMonstersSkGnBot", "Sky Garden (bottom)"],
    6: ["CardMonstersMu", "Mu"],
    7: ["CardMonstersAngl", "Angel Dungeon"],
    8: ["CardMonstersGtWl", "Great Wall"],
    9: ["CardMonstersKres", "Mt. Kress"],
    10: ["CardMonstersAnkrOuter", "Ankor Wat (outside)"],
    11: ["CardMonstersAnkrInner", "Ankor Wat (inside)"],
    12: ["CardMonstersPymd", "Pyramid"],
    13: ["CardMonstersJwlr", "Jeweler's Mansion"]
}
