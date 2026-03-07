from typing import Mapping, Any

# Logic requirements for exits to be traversable. For more complex logic, manually create an artificial node.
# During initialization, new nodes are created and entries are added to self.logic as needed.
# If IsCoupled, the logic will be applied to the coupled exit too.
# Format: { ID: [0: ExitId,
#                1: [[item1, qty1],[item2,qty2],...],
#                2: Direction (0 = to exit from node, 1 = from exit to node, 2 = both),
#                3: IsCoupled
#               ] }
def get_exit_logic(allow_glitches: bool = False) -> Mapping[int, list[Any]]:
    # TODO: Gets mutated, Consider turning into a class [int, list[list[int]], int, bool]
    return {
        1: [62, [[701, 1]], 0, False],  # Edward's first worm door
        2: [64, [[702, 1]], 0, False],  # Edward's second worm door
        3: [68, [[703, 1]], 0, False],  # Edward's bat door
        4: [70, [[501, 1], [609, 1]], 0, False],  # Edward's Lilly door requires Lilly and an attack
        5: [90, [[608, 1]], 0, False],  # Itory cave wall
        6: [152, [[8, 1], [611, 1]], 0, False],  # Inca Golden Tile
        7: [126, [[524, 1]], 2, False],  # Inca Diamond Block
        52: [118, [[612, 1]], 0, False],  # Inca statue puzzle requires pulling the statues
        8: [234, [[528, 1]], 0, False],  # Mine tunnel wall
        9: [224, [[15, 1]], 0, False],  # Mine elevator
        50: [226, [[609, 1]], 0, False],  # Mine big room requires hitting buttons
        10: [246, [[11, 1], [12, 1]], 0, False],  # Mine end
        51: [287, [[609, 1], [612, 1]], 0, False],  # Sky Garden to blue room requires moving the statue
        11: [310, [[16, 1]], 0, True],  # Sea Palace door
        12: [354, [[511, 1]], 2, False],  # Mu-NW door (Hope Room)
        13: [362, [[512, 1]], 2, True],  # Mu-NW/W exit (Bot)
        14: [356, [[62, 1], [801, 1]], 0, True],  # Mu-NW/W Slider hole, blocked for dungeon construction
        15: [360, [[512, 1]], 2, True],  # Mu-NE/E exit 1 (Bot)
        16: [340, [[511, 1]], 2, True],  # Mu-NE/E exit 2 (Mid)
        17: [358, [[512, 1]], 2, True],  # Mu-E/W exit 1 (Bot)
        18: [342, [[511, 1]], 2, True],  # Mu-E/W exit 2 (Mid)
        19: [352, [[511, 1]], 2, True],  # Mu-W/SW exit 1 (Mid)
        20: [364, [[512, 1]], 2, True],  # Mu-W/SW exit 2 (Bot)
        21: [346, [[511, 1]], 2, True],  # Mu-W/SW exit 3 (Mid)
        22: [348, [[511, 1]], 2, True],  # Mu-SW/SE exit 1 (Mid)
        23: [366, [[512, 1]], 2, True],  # Mu-SW/SE exit 2 (Bot)
        24: [350, [[511, 1]], 2, True],  # Mu-SW/SE exit 3 (Mid)
        25: [368, [[512, 1]], 2, False],  # Mu-SE exit door (Bot)
        26: [408, [[62, 1]], 0, True],  # Angl chest slider
        27: [414, [[62, 1]], 0, True],  # Angl Ishtar slider
        28: [591, [] if allow_glitches else [[28, 1]], 2, False],  # Wat bright room N
        29: [575, [[609, 1]], 2, False],  # Garden S requires a weapon to pass the bushes
        32: [576, [[609, 1]], 2, False],  # Garden N requires a weapon to pass the bushes
        30: [592, [] if allow_glitches else [[28, 1]], 2, False],  # Wat bright room S
        31: [ 704, [[522, 1]], 0, False ],   # MQ2 upper door
    }
