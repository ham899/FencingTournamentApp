from dataclasses import dataclass
from enum import Enum, auto

import validation

from entities.tournament_entry import TournamentEntry


class DEEntryStatus(Enum):
    """
    Represent an entry's participation status within a DE bracket.

    Attributes
    ----------
    WINNER
        The entry has won the DE bracket.
    ACTIVE
        The entry has not been eliminated from the DE bracket. 
        In a stopped bracket, 
        this includes an entry that has reached the stopping round and qualified to advance.
    ELIMINATED
        The entry can no longer win this bracket.
        It may still participate in the bracket's separate third-place matchup
        or compete in a separate consolation bracket.
    """
    WINNER = auto()
    ACTIVE = auto()
    ELIMINATED = auto()


@dataclass(frozen=True, slots=True)
class DEEntryResult:
    """
    Represent a single entry's calculated result snapshot for a DE bracket.

    This object's fields cannot be reassigned after initialization.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose bracket results are represented.
    stage_number : int
        The containing DE stage's one-based position within the tournament.
    bracket_seed : int
        The entry's one-based starting seed within this DE bracket.
    previous_place : int | None
        The entry's placement in the preceding tournament stage.
        None if no previous placement is available.
        Equal non-None values preserve incoming ties for entries eliminated in the same round, 
        unless a placement match determines their order.
    round_reached : int
        The one-based number of the furthest bracket round reached.
        Participation in the separate third-place matchup does not change this value.
    place : int | None
        The entry's confirmed finishing position within this DE bracket,
        or None if its exact position has not yet been determined.
    status : DEEntryStatus
        The entry's participation status within this DE bracket.
    """
    entry: TournamentEntry
    stage_number: int
    bracket_seed: int
    previous_place: int | None
    round_reached: int
    place: int | None
    status: DEEntryStatus


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the entry, stage number, bracket seed, previous placement, round reached, finishing place, and status.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry,
            stage_number, bracket_seed, or round_reached is not an integer,
            previous_place or place is neither an integer nor None,
            or status is not a DEEntryStatus.
        ValueError
            If stage_number, bracket_seed, or round_reached is not positive,
            previous_place or place is not positive when provided,
            or status and place are inconsistent.
        """
        location = self.__class__.__name__

        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(f'Entry must be a TournamentEntry in {location} - got {type(self.entry).__name__}')
        
        validation.validate_positive_int(self.stage_number, 'Stage number', location)
        validation.validate_positive_int(self.bracket_seed, 'Bracket seed', location)
        validation.validate_optional_positive_int(self.previous_place, 'Previous place', location)
        validation.validate_positive_int(self.round_reached, 'Round reached', location)
        validation.validate_optional_positive_int(self.place, 'Place', location)

        if not isinstance(self.status, DEEntryStatus):
            raise TypeError(f'Status must be a DEEntryStatus in {location} - got {type(self.status).__name__}')
        
        self._validate_status_place_relationship(self.status, self.place, location)


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID of this result."""
        return self.entry.tournament_id

    @property
    def display_name(self) -> str:
        """Return the display name of the represented entry."""
        return self.entry.display_name


    # --- Validation Helper Methods ---
    def _validate_status_place_relationship(self, status: DEEntryStatus, place: int | None, location: str) -> None:
        """
        Validate that the participation status and finishing place agree.

        Parameters
        ----------
        status : DEEntryStatus
            The entry's participation status within the DE bracket.
        place : int | None
            The entry's confirmed finishing position within the DE bracket,
            or None if its exact position has not yet been determined.
        location : str
            The name of the calling method or class for error message context.

        Raises
        ------
        ValueError
            If a winner does not have place 1, an active entry has a confirmed place, or an eliminated entry has place 1.
        """
        # Validate status guarantees
        if status == DEEntryStatus.WINNER and place != 1:
            raise ValueError(
                f'Winner must have place 1 in {location} - got place {place} for entry ID {self.entry.id}'
            )
            
        elif status == DEEntryStatus.ACTIVE and place is not None:
            raise ValueError(
                f'Active entry cannot have a confirmed finishing place in {location} - '
                f'got place {place} for entry ID {self.entry.id}'
            )

        elif status == DEEntryStatus.ELIMINATED and place == 1:
            raise ValueError(
                f'Eliminated entry (ID {self.entry.id}) cannot have place 1 in {location}'
            )
