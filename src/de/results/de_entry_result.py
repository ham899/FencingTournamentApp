from dataclasses import dataclass
from enum import Enum, auto

import validation

from entities.tournament_entry import TournamentEntry


class DEEntryStatus(Enum):
    """
    Represent an entry's participation status within a DE stage.

    Attributes
    ----------
    WINNER
        The entry has won the entire DE stage.
    ACTIVE
        The entry remains in contention to win the DE stage.
    ELIMINATED
        The entry has been eliminated from the DE stage.
    """
    WINNER = auto()
    ACTIVE = auto()
    ELIMINATED = auto()


@dataclass(frozen=True, slots=True)
class DEEntryResult:
    """
    Represent a single entry's calculated result snapshot for a DE stage.

    This object's fields cannot be reassigned after initialization.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose DE results are represented.
    stage_number : int
        The DE stage's one-based position within the tournament.
    bracket_seed : int
        The entry's one-based starting seed within this DE stage.
    round_reached : int
        The one-based number of the furthest DE round reached within this bracket.
    place : int | None
        The entry's confirmed finishing position within this DE stage, or None if its exact position is not yet determined.
    status : DEEntryStatus
        The entry's participation status within this DE stage.
    """  
    entry: TournamentEntry
    stage_number: int
    bracket_seed: int
    round_reached: int
    place: int | None
    status: DEEntryStatus


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the supplied entry, stage number, seed, round reached, place, and status.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, stage_number, bracket_seed, or round_reached is not an integer, 
            place is neither an integer nor None, or status is not a DEEntryStatus.
        ValueError
            If stage_number, bracket_seed, or round_reached is not positive, place is not positive when provided, 
            or status and place are inconsistent with each other.
        """
        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(f'Entry must be a TournamentEntry in DEEntryResult - got {type(self.entry).__name__}')
        
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DEEntryResult')
        validation.validate_positive_int(self.bracket_seed, 'DE seed', 'DEEntryResult')
        validation.validate_positive_int(self.round_reached, 'Round reached', 'DEEntryResult')
        validation.validate_optional_positive_int(self.place, 'Place', 'DEEntryResult')

        if not isinstance(self.status, DEEntryStatus):
            raise TypeError(f'Status must be a DEEntryStatus in DEEntryResult - got {type(self.status).__name__}')
        
        self._validate_status_place_relationship(self.status, self.place)


    # --- Validation Helper Methods ---
    def _validate_status_place_relationship(self, status: DEEntryStatus, place: int | None) -> None:
        """
        Validate that the participation status and finishing place agree.

        Parameters
        ----------
        status : DEEntryStatus
            The entry's participation status within the DE stage.
        place : int | None
            The entry's confirmed finishing position, or None if its exact position is not yet determined.

        Raises
        ------
        ValueError
            If a winner does not have place 1, an active entry has a confirmed place, or an eliminated entry has place 1.
        """
        # Validate status guarantees
        if status == DEEntryStatus.WINNER and place != 1:
            raise ValueError(f'Winner must have place 1 in DEEntryResult - got place {place} for entry ID {self.entry.id}')
            
        elif status == DEEntryStatus.ACTIVE and place is not None:
            raise ValueError(f'Active entry cannot have a confirmed finishing place in DEEntryResult - got place {place} for entry ID {self.entry.id}')
            
        elif status == DEEntryStatus.ELIMINATED and place == 1:
            raise ValueError(f'Eliminated entry (ID {self.entry.id}) cannot have place 1 in DEEntryResult')
