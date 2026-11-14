from dataclasses import dataclass
from enum import Enum, auto

import validation

from entities.tournament_entry import TournamentEntry


class TournamentEntryStatus(Enum):
    """
    Represent an entry's status in the overall tournament.

    Attributes
    ----------
    WINNER
        The entry is recognized as a tournament winner and has a confirmed final place of 1.
    ACTIVE
        The entry has not been eliminated or declared a tournament winner.
        This includes entries awaiting a later stage and 
        a champion awaiting tournament completion before receiving WINNER status.
        No final tournament place is assigned in the snapshot.
    ELIMINATED
        The entry is out of contention for the tournament title.
        It may still fence a classification bout, and its final place may be unconfirmed.
    
    Notes
    -----
    TournamentResults assigns WINNER status only when the entire tournament is complete.
    """
    WINNER = auto()
    ACTIVE = auto()
    ELIMINATED = auto()


@dataclass(frozen=True, slots=True)
class TournamentEntryResult:
    """
    Represent a snapshot of an entry's overall tournament standing.

    Place represents a confirmed final tournament placement, 
    rather than a current ranking or a placement within an individual stage.

    Fields cannot be reassigned after initialization.
    The tournament entry is retained by reference rather than copied.

    Attributes
    ----------
    entry : TournamentEntry
        The entry represented by this snapshot.
    stage_reached : int
        The one-based number of the latest stage the entry has entered.
        Qualifying for a stage that has not yet begun does not increase this value.
    status : TournamentEntryStatus
        The entry's status within the overall tournament.
    place : int | None
        The entry's confirmed one-based final tournament placement.
        Entries tied in the final standings may share a place.
        None if no final placement has been confirmed in this snapshot.

    Notes
    -----
    WINNER requires place 1.
    ACTIVE requires place None.
    ELIMINATED permits place None or a place greater than 1.

    This class validates individual field values and their consistency.
    It does not calculate standings, verify stage participation, 
    or compare placements across entries.
    """
    entry: TournamentEntry
    stage_reached: int
    status: TournamentEntryStatus
    place: int | None


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the supplied fields and status-placement relationship.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, if stage_reached is not an integer,
            if status is not a TournamentEntryStatus, or if place is neither an integer nor None.
        ValueError
            If stage_reached is not positive, if place is not positive when provided,
            if WINNER does not have place 1, if ACTIVE has an assigned place, or if ELIMINATED has place 1.
        """
        location = self.__class__.__name__

        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry in {location} - got {type(self.entry).__name__}'
            )

        validation.validate_positive_int(self.stage_reached, 'Stage reached', location)

        if not isinstance(self.status, TournamentEntryStatus):
            raise TypeError(
                f'Status must be a TournamentEntryStatus in {location} - got {type(self.status).__name__}'
            )

        validation.validate_optional_positive_int(self.place, 'Place', location)

        self._validate_status_place_relationship(self.status, self.place, location)


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the ID of the tournament represented by this result."""
        return self.entry.tournament_id

    @property
    def display_name(self) -> str:
        """Return the display name of the represented entry."""
        return self.entry.display_name


    # --- Validation Helper Methods ---
    def _validate_status_place_relationship(self, status: TournamentEntryStatus, place: int | None, location: str) -> None:
        """
        Validate that the status and confirmed placement are consistent.

        Assume the individual arguments have already been validated.

        Parameters
        ----------
        status : TournamentEntryStatus
            The entry's overall tournament status.
        place : int | None
            The confirmed final tournament placement, or None.
        location : str
            The calling class name used in validation error messages.

        Raises
        ------
        ValueError
            If WINNER does not have place 1,
            if ACTIVE has an assigned place,
            or if ELIMINATED has place 1.
        """
        if status == TournamentEntryStatus.WINNER and place != 1:
            raise ValueError(
                f'A status of WINNER and a place of 1st must coincide in {location}'
                f' - got status={status}, place={place}'
            )
        
        if status == TournamentEntryStatus.ACTIVE and place is not None:
            raise ValueError(
                f'A status of ACTIVE cannot have a confirmed place in {location}'
                f' - got status={status}, place={place}'
            )
        
        if status == TournamentEntryStatus.ELIMINATED and place == 1:
            raise ValueError(
                f'An eliminated entry cannot have a final placement of 1st place in {location}'
                f' - got status={status}, place={place}'
            )
