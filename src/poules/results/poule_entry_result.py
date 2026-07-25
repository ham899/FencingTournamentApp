from dataclasses import dataclass

import validation

from entities.tournament_entry import TournamentEntry


@dataclass(frozen=True, slots=True)
class PouleEntryResult:
    """
    Represents a single entry's calculated result snapshot for a poule.

    The statistics are calculated from completed poule matches by `PouleResult`.
    This object's fields cannot be reassigned after initialization.

    **Note:** An entry with no completed bouts has a victory ratio of 0.0.
    
    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose poule results are represented.
    poule_id : int
        The unique identifier of the poule containing the entry.
    tournament_id : int
        The unique identifier of the tournament containing the poule.
    num_matches : int
        The number of completed poule bouts fenced by the entry.
    num_victories : int
        The number of completed poule bouts won by the entry.
    touches_scored : int
        The total number of touches scored by the entry in completed poule bouts.
    touches_received : int
        The total number of touches scored against the entry in completed poule bouts.
    """
    entry: TournamentEntry
    poule_id: int
    tournament_id: int
    num_matches: int
    num_victories: int
    touches_scored: int
    touches_received: int


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the class input data.

        Raises
        ------
        TypeError
            If `entry` is not a TournamentEntry, or if `poule_id`, `tournament_id`, `num_matches`, `num_victories`, 
            `touches_scored`, or `touches_received` is not an integer.
        ValueError
            If `poule_id` or `tournament_id` is not positive, if the entry belongs
            to another tournament, if a result statistic is negative, if the number
            of victories exceeds the number of matches, or if touches are recorded
            when no matches have been completed.
        """
        # Validate the provided tournament and poule IDs first before the entry
        validation.validate_positive_int(self.tournament_id, 'tournament ID', 'PouleEntryResult')
        validation.validate_positive_int(self.poule_id, 'poule ID', 'PouleEntryResult')
        
        # Validate the provided entry
        self._validate_entry(self.entry)

        # Validate the provided entry results
        validation.validate_non_negative_int(self.num_matches, 'number of matches', 'PouleEntryResult')
        validation.validate_non_negative_int(self.num_victories, 'number of victories', 'PouleEntryResult')
        validation.validate_non_negative_int(self.touches_scored, 'touches scored', 'PouleEntryResult')
        validation.validate_non_negative_int(self.touches_received, 'touches received', 'PouleEntryResult')

        # Validate that result statistics are possible
        if self.num_victories > self.num_matches:
            raise ValueError(f'Number of victories cannot be greater than the number of matches in PouleEntryResult - got {self.num_victories} victories and {self.num_matches} matches')
        
        if self.num_matches == 0:
            if self.touches_scored > 0:
                raise ValueError(f'Touches scored cannot be greater than 0 when the entry has completed no matches - got {self.touches_scored} touches scored and {self.num_matches} matches')
            
            if self.touches_received > 0:
                raise ValueError(f'Touches received cannot be greater than 0 when the entry has completed no matches - got {self.touches_received} touches received and {self.num_matches} matches')


    # --- Properties ---
    @property
    def display_name(self) -> str:
        """Returns the display name of the entry."""
        return self.entry.display_name

    @property
    def victory_ratio(self) -> float:
        """Returns the entry's victory ratio, or 0.0 if no completed matches exist."""
        return 0.0 if self.num_matches == 0 else self.num_victories / self.num_matches
    
    @property
    def indicator(self) -> int:
        """Returns touches scored minus touches received for the entry."""
        return self.touches_scored - self.touches_received


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry) -> None:
        """
        Validate the result data and ensure its statistics are consistent.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, or if the entry's tournament ID is not an integer.
        ValueError
            If the entry's tournament ID is not positive or does not match this result's tournament_id.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be TournamentEntry in PouleEntryResult - got {type(entry).__name__}')
        
        validation.validate_positive_int(entry.tournament_id, 'Entry tournament ID', 'PouleEntryResult')

        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry tournament ID {entry.tournament_id} does not match the provided tournament ID {self.tournament_id} in this PouleEntryResult')