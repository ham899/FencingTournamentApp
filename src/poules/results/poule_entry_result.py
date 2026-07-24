from collections.abc import Iterable
from dataclasses import dataclass, field, InitVar

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch


@dataclass(frozen=True, slots=True)
class PouleEntryResult:
    """
    Represents a single entry's derived results from completed bouts in a poule.

    A PouleEntryResult is calculated from completed PouleMatch objects; matches
    remain the source of truth for the underlying bout results.

    **Note:** An entry with no completed bouts has a victory ratio of 0.0.

    Parameters
    ----------
    entry : TournamentEntry
        The tournament entry whose results are represented.
    poule_id : int
        The identifier of the entry's poule.
    tournament_id : int
        The identifier of the entry's tournament.
    poule_matches : Iterable[PouleMatch]
        The poule matches from which to calculate the statistics. The matches
        themselves are not stored.
    
    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose poule results are represented.
    poule_id : int
        The unique identifier of the poule containing the entry.
    tournament_id : int
        The unique identifier of the tournament containing the poule.
    num_matches : int, init=False
        The number of completed poule bouts fenced by the entry.
    num_victories : int, init=False
        The number of completed poule bouts won by the entry.
    touches_scored : int, init=False
        The total number of touches scored by the entry in completed poule bouts.
    touches_received : int, init=False
        The total number of touches scored against the entry in completed poule bouts.
    """
    entry: TournamentEntry
    poule_id: int
    tournament_id: int

    poule_matches: InitVar[Iterable[PouleMatch]]

    num_matches: int = field(init=False)
    num_victories: int = field(init=False)
    touches_scored: int = field(init=False)
    touches_received: int = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, poule_matches: Iterable[PouleMatch]) -> None:
        """
        Validate the inputs and calculate the entry's result statistics.

        Raises
        ------
        TypeError
            If `entry` is not a TournamentEntry, if `poule_id` or
            `tournament_id` is not an integer, if `poule_matches` is not an
            iterable, or if it contains an item that is not a PouleMatch.
        ValueError
            If `poule_id` or `tournament_id` is not positive, if the entry belongs 
            to another tournament, if no matches are provided, if a match has a 
            different poule or tournament ID, or if a match ID occurs more than once.
        RuntimeError
            If a completed match involving the entry does not have a valid winner index.
        """
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleEntryResult')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleEntryResult')

        self._validate_entry(self.entry)

        if not isinstance(poule_matches, Iterable):
            raise TypeError(f'poule_matches must be a valid iterable - got {type(poule_matches).__name__}')
        
        poule_matches = tuple(poule_matches) # Convert poule matches into a tuple before validating

        self._validate_matches(poule_matches)

        # Extract the result info
        num_matches, num_victories, touches_scored, touches_received = self._calculate_results_from_matches(poule_matches)

        # Set result attributes
        object.__setattr__(self, 'num_matches', num_matches)
        object.__setattr__(self, 'num_victories', num_victories)
        object.__setattr__(self, 'touches_scored', touches_scored)
        object.__setattr__(self, 'touches_received', touches_received)


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


    # --- Result Calculation Helper Methods ---
    def _calculate_results_from_matches(self, matches: tuple[PouleMatch, ...]) -> tuple[int, int, int, int]:
        """
        Calculates the key poule result metrics from the provided poule matches.
        
        Parameters
        ----------
        matches : tuple[PouleMatch, ...]
            The matches to compute the results from.

        Returns
        -------
        tuple[int, int, int, int]
            Four integer values representing the calculated values: 
            number of matches, number of victories, touches scored, and touches received respectively.
        """
        # Set counter variables to zero
        num_matches = 0
        num_victories = 0
        touches_scored = 0
        touches_received = 0

        for match in matches:
            if match.is_complete() and match.has_entry(self.entry):
                # Identify whether this entry is entry 1 or 2
                entry_index = 0 if match.entry1 == self.entry else 1

                # Extract the winner index of the match
                winner_index = match.winner_index()

                if winner_index not in (0, 1):
                    raise RuntimeError(f'Completed poule match {match.id} has an invalid winner index of {winner_index} in PouleEntryResult._calculate_results_from_matches().')

                # Add match result information
                num_matches += 1
                num_victories += 1 if entry_index == winner_index else 0
                touches_scored += match.score1 if entry_index == 0 else match.score2
                touches_received += match.score2 if entry_index == 0 else match.score1

        return num_matches, num_victories, touches_scored, touches_received


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry) -> None:
        """
        Validates that an entry is a TournamentEntry belonging to this result's tournament.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry.
        ValueError
            If the entry's tournament ID is not positive or does not match tournament_id.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry in PouleEntryResult - got {type(entry).__name__}')
        
        validation.validate_positive_int(entry.tournament_id, 'Entry Tournament ID', 'PouleEntryResult', '_validate_entry')

        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry tournament ID {entry.tournament_id} does not match the provided tournament ID {self.tournament_id} in PouleEntryResult')
        
    def _validate_matches(self, matches: tuple[PouleMatch, ...]) -> None:
        """
        Validate the poule matches used to calculate this entry's results.

        Parameters
        ----------
        matches : tuple[PouleMatch, ...]
            The poule matches to validate.

        Raises
        ------
        TypeError
            If `matches` is not a tuple or contains an item that is not a
            PouleMatch.
        ValueError
            If `matches` is empty, if a match has a different poule or
            tournament ID, or if a match ID occurs more than once.
        """
        if not isinstance(matches, tuple):
            raise TypeError(f'The provided matches must be a tuple - got {type(matches).__name__}')
        
        if not matches:
            raise ValueError(f'There must be at least one match present in the tuple - got {len(matches)}')
        
        seen_match_ids: set[int] = set()

        for i, match in enumerate(matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'The entry at index {i} in `matches` must be a PouleMatch object - got {type(match).__name__}')

            if match.poule_id != self.poule_id:
                raise ValueError(f'The poule match at index {i} in `matches` does not have the same poule ID {match.poule_id} as the poule ID of this result {self.poule_id}')
            
            if match.tournament_id != self.tournament_id:
                raise ValueError(f'The poule match at index {i} in `matches` does not have the same tournament ID {match.tournament_id} as the tournament ID this result {self.tournament_id}')
            
            if match.id in seen_match_ids:
                raise ValueError(f'Poule match ID {match.id} occurs more than once.')

            seen_match_ids.add(match.id)