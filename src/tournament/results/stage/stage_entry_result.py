from abc import ABC, abstractmethod
from dataclasses import dataclass

import validation

from entities import Fencer, TournamentEntry
from tournament.results.stage.stage_entry_status import StageEntryStatus


@dataclass(frozen=True, slots=True)
class StageEntryResult(ABC):
    """
    Represent a snapshot of an entry's standing within a tournament stage.

    Provide common result fields and validation for stage-specific subclasses.
    Subclasses must implement the ``label`` property.

    Position identifies the entry's unique one-based index in the containing stage snapshot's ranked_results. 
    It provides an ordering even when the entry's placement is unresolved and may change between snapshots.

    Place represents a confirmed placement within this stage, not necessarily a final tournament placement. 
    Multiple entries may share a confirmed place. A stage may confirm some placements before the entire stage is complete.

    Fields cannot be reassigned after initialization.
    The tournament entry is retained by reference rather than copied.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose stage standing is represented.
    stage_number : int
        The stage's one-based position within the tournament.
    status : StageEntryStatus
        The entry's participation or elimination status within the stage.
        Status does not by itself indicate whether a placement is confirmed.
    position : int
        The entry's unique one-based index in the stage snapshot's ranked_results.
        Defines display order and the relative seeding order of advancing entries.
        Does not imply a confirmed placement.
    place : int | None
        The entry's confirmed one-based placement within the stage.
        Entries with a confirmed tie share the same place.
        None while the placement is unresolved.
    is_tie : bool | None
        Whether the confirmed place is shared with another entry.
        None exactly when place is None.

    Notes
    -----
    The containing stage-results calculation assigns positions consecutively from 1 and determines placements and ties. 
    This class validates individual field values but cannot verify ordering, uniqueness, or ties across entries.

    ``place`` and ``is_tie`` must either both be assigned or both be None.
    """
    entry: TournamentEntry
    stage_number: int
    status: StageEntryStatus
    position: int
    place: int | None
    is_tie: bool | None


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the common stage-entry result fields.

        Subclasses that override this method must also call this implementation
        to validate the inherited fields.

        Raises
        ------
        TypeError
            If the entry or its checked attributes have invalid types,
            if ``status`` is not a StageEntryStatus, 
            if ``stage_number`` or ``position`` is not an integer, 
            if ``place`` is neither an integer nor None, 
            or if ``is_tie`` is neither a boolean nor None.
        ValueError
            If a required integer is not positive, 
            or if exactly one of ``place`` and ``is_tie`` is None.
        """
        location = self.__class__.__name__

        self._validate_entry(self.entry, location)
        validation.validate_positive_int(self.stage_number, 'stage_number', location)
        validation.validate_positive_int(self.position, 'position', location)
        validation.validate_optional_positive_int(self.place, 'place', location)
        validation.validate_optional_bool(self.is_tie, 'is_tie', location)
        self._validate_place_is_tie_relationship(self.place, self.is_tie, location)

        if not isinstance(self.status, StageEntryStatus):
            raise TypeError(
                f'Status must be a StageEntryStatus in {location} - got {type(self.status).__name__}'
            )


    # --- Properties ---
    @property
    @abstractmethod
    def label(self) -> str:
        """Return a descriptive label for the entry's result in the stage."""
        pass

    @property
    def display_name(self) -> str:
        """Return the display name of the entry."""
        return self.entry.display_name

    @property
    def tournament_id(self) -> int:
        """Return the ID of the tournament to which the entry belongs."""
        return self.entry.tournament_id


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry, location: str) -> None:
        """
        Validate the referenced tournament entry and its required attributes.

        Parameters
        ----------
        entry : TournamentEntry
            The entry to validate.
        location : str
            The class name to include in validation error messages.

        Raises
        ------
        TypeError
            If ``entry`` is not a TournamentEntry, if its ID or tournament ID is not an integer, 
            if its display name is not a string, or if its fencer is not a Fencer.
        ValueError
            If the entry's ID or tournament ID is not positive.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry in {location} - got {type(entry).__name__}'
            )
        
        validation.validate_positive_int(entry.id, 'Entry ID', location)
        validation.validate_positive_int(entry.tournament_id, f'Entry {entry.id} tournament ID', location)
        validation.validate_string(entry.display_name, f'Entry {entry.id} display name', location)

        if not isinstance(entry.fencer, Fencer):
            raise TypeError(
                f'Entry {entry.id} fencer must be a Fencer in {location} - got {type(entry.fencer).__name__}'
            )

    def _validate_place_is_tie_relationship(self, place: int | None, is_tie: bool | None, location: str) -> None:
        """
        Validate that placement and tie information are assigned together.

        This method assumes the individual values have already been validated.
        It does not check whether another entry actually shares the placement.

        Parameters
        ----------
        place : int | None
            The entry's confirmed placement, or None if unassigned.
        is_tie : bool | None
            Whether the confirmed placement is tied, or None if unassigned.
        location : str
            The class name to include in validation error messages.

        Raises
        ------
        ValueError
            If exactly one of ``place`` and ``is_tie`` is None.
        """
        if (place is None) != (is_tie is None):
            raise ValueError(
                f'Place and is_tie must either both be assigned or both be None in {location} - got place={place}, is_tie={is_tie}'
            )
