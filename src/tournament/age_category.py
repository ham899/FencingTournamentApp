from enum import Enum, auto


class AgeCategory(Enum):
    """Identify the age division of a fencing tournament."""
    Y8 = auto()
    Y10 = auto()
    Y12 = auto()
    Y14 = auto()
    CADET = auto()
    JUNIOR = auto()
    OPEN = auto()
    VETERAN = auto()
