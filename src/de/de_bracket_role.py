from enum import Enum, auto


class DEBracketRole(Enum):
    """Represent a bracket's role within a direct-elimination stage."""

    MAIN = auto()
    CONSOLATION = auto()
