from typing import Final, Mapping

# List of disallowed enemy types at each monster ID, for ensuring that orbs are reachable
# and solid monsters can't softlock you, etc.
ENEMIZER_RESTRICTED_ENEMIES: Final[Mapping[int, list[int]]] = {
    0x0004: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Skeleton Cage
    0x0006: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel First Door
    0x0016: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Second Door
    0x002A: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Bat Door
    0x0034: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Dark Space
    0x0043: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Skeleton Door 1
    0x0044: [53, 60, 73, 80, 81, 102, 103, 104],  # U.Tunnel Skeleton Door 2
    0x0051: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca West Ladder
    0x0052: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca Entrance Ladder
    0x0055: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca Final Ladder
    0x007A: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca N/S Ramp Room Ramp
    0x009D: [14, 33, 52, 53, 60, 73, 80, 81, 102, 103, 104, 143],  # Inca E/W Ramp Room Ramp
    0x00BF: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca Diamond Block Stair
    0x00CA: [53, 60, 73, 80, 81, 102, 103, 104],  # Inca Singing Statue Stair
    0x00CF: [53, 60, 73, 80, 81, 102, 103, 104],  # Mine Tunnel Middle Fence
    0x00D2: [53, 60, 73, 80, 81, 102, 103, 104],  # Mine Tunnel South Fence
    0x00D3: [53, 60, 73, 80, 81, 102, 103, 104],  # Mine Tunnel North Fence
    0x00E0: [53, 60, 73, 80, 81, 102, 103, 104],  # Mine Big Room Cage
    0x00FD: [53, 60, 73, 80, 81, 102, 103, 104],  # Mine Appearing Dark Space
    # 0x0102: [],   # Friar worm fence worm is never randomized
    0x013B: [2, 14, 17, 22, 33, 35, 41, 43, 52, 53, 55, 60, 62, 73, 80, 81, 102, 103, 104, 123, 141, 143],
    # Garden SE Top Gate
    0x0148: [53, 60, 73, 80, 81, 102, 103, 104],  # Garden SE Darkside Chest
    0x0150: [53, 60, 73, 80, 81, 102, 103, 104],  # Garden SW Top Robot Gate
    0x0153: [53, 60, 73, 80, 81, 102, 103, 104],  # Garden SW Top Robot Ramp
    0x015C: [53, 60, 73, 80, 81, 102, 103, 104],  # Garden SW Top Worm Gate
    0x0161: [53, 60, 73, 80, 81, 102, 103, 104],  # Garden SW Darkside Cage
    0x0194: [53, 60, 73, 80, 81, 102, 103, 104],  # Mu Entrance Gate
    0x01A7: [2, 14, 17, 22, 33, 35, 41, 43, 52, 53, 55, 60, 62, 73, 80, 81, 102, 103, 104, 123, 141, 143],
    # Mu NE First Rock
    0x01A9: [2, 14, 17, 22, 33, 35, 41, 43, 52, 53, 55, 60, 62, 73, 80, 81, 102, 103, 104, 123, 141, 143],
    # Mu NE Second Rock
    0x01DE: [53, 60, 73, 80, 81, 102, 103, 104],  # Mu West Slime Cages
    0x01EE: [53, 60, 73, 80, 81, 102, 103, 104],  # Mu SE East-facing Head
    0x01FC: [53, 60, 73, 80, 81, 102, 103, 104],  # Mu SE South-facing Head
    0x029B: [2, 14, 17, 22, 33, 35, 41, 43, 52, 53, 55, 60, 62, 73, 80, 81, 102, 103, 104, 123, 141, 143],
    # Great Wall Friar Gate
    # 0x02B6: [],   # Fanger is never randomized
    0x030A: [53, 60, 73, 80, 81, 102, 103, 104],  # Kress West Room Shortcut
    0x0388: [53, 60, 73, 80, 81, 102, 103, 104],  # Wat Entrance Stair
    0x0395: [53, 60, 73, 80, 81, 102, 103, 104],  # Wat East Slider Hole
    0x03A0: [53, 60, 73, 80, 81, 102, 103, 104],  # Ankor Wat Pit Exit
    0x03E9: [2, 14, 17, 22, 33, 35, 41, 43, 52, 53, 55, 60, 62, 73, 80, 81, 102, 103, 104, 123, 141, 143],
    # Wat Dark Space Corridor
    0x0417: [53, 60, 73, 80, 81, 102, 103, 104],  # Pyramid Foyer Dark Space
    0x04FA: [53, 60, 73, 80, 81, 102, 103, 104],  # Mansion First Barrier
    0x0505: [53, 60, 73, 80, 81, 102, 103, 104]  # Mansion Second Barrier
}
