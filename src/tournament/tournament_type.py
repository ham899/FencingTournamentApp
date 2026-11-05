"""Define the tournament formats supported by the application."""

from enum import Enum, auto


class TournamentType(Enum):
    """
    Identify a tournament's stage sequence.

    POULE_DE_POULE_DE uses a stopped first DE stage, 
    followed by another poule stage and a final DE stage.
    """
    POULE = auto()
    DE = auto()
    POULE_DE = auto()
    POULE_DE_POULE_DE = auto()
