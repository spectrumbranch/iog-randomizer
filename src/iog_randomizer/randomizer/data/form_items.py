from typing import Final, Mapping

# Items that transfer DS and form access.
# Items not in any list are assumed to be form-independent.
FORM_ITEMS: Final[Mapping[int, list[int]]] = {
    0: [61, 62, 63],  # Will
    1: [64, 65, 66],  # Freedan
    2: [36, 67]  # Shadow - Aura and Firebird
}
