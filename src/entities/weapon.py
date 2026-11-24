from enum import Enum, auto


class Weapon(Enum):
    """Identify the weapon used in a fencing bout."""
    FOIL = auto()
    EPEE = auto()
    SABRE = auto()
