from enum import Enum, auto


class StageEntryStatus(Enum):
    """
    Represent an entry's elimination status within a tournament stage.

    Status describes whether the entry has been eliminated, 
    independently of whether the stage is complete or another stage follows.

    Attributes
    ----------
    ACTIVE
        The entry has not been eliminated in the stage.
        This includes entries still competing and entries that remain after the stage is complete, 
        including the stage winner.
        It does not necessarily mean the entry has matches remaining.
    ELIMINATED
        The entry has been eliminated by the stage's competition or cut rules and 
        is not eligible to advance to a subsequent stage.
        It does not necessarily mean all placement matches are complete.
    """
    ACTIVE = auto()
    ELIMINATED = auto()
