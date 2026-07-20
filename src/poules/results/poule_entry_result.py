from dataclasses import dataclass, field

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch


@dataclass
class PouleEntryResult:
    """
    Represents a single entry's derived results from completed bouts in a poule.

    A PouleEntryResult is calculated from completed PouleMatch objects; matches
    remain the source of truth for the underlying bout results.

    **Note:** An entry with no completed bouts has a victory ratio of 0.0.

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

    num_matches: int = field(default=0, init=False)
    num_victories: int = field(default=0, init=False)
    touches_scored: int = field(default=0, init=False)
    touches_received: int = field(default=0, init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the initialized PouleEntryResult attributes.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, or if poule_id or tournament_id is not an integer.
        ValueError
            If poule_id or tournament_id is not positive, or if entry belongs to a different tournament.
        """       
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleEntryResult')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleEntryResult')
        self._validate_entry(self.entry)


    # --- Properties ---
    @property
    def display_name(self) -> str:
        """Returns the display name of the entry."""
        return self.entry.display_name

    @property
    def ratio(self) -> float:
        """Returns the entry's victory ratio, or 0.0 if no completed matches exist."""
        return 0.0 if self.num_matches == 0 else self.num_victories / self.num_matches
    
    @property
    def indicator(self) -> int:
        """Returns touches scored minus touches received for the entry."""
        return self.touches_scored - self.touches_received


    # --- State Update Helper Methods ---
    def _reset(self) -> None:
        """Resets all the entry's results back to zero - **use carefully**."""
        self.num_matches = 0
        self.num_victories = 0
        self.touches_scored = 0
        self.touches_received = 0


    # --- Result Calculation Helper Methods ---
    def _add_match_result(self, match: PouleMatch) -> None:
        """
        Adds the applicable result from a completed poule match to this entry's totals.

        If the match does not involve this entry, this method does nothing. This method
        is intended for internal use while calculating poule results.

        Parameters
        ----------
        match : PouleMatch
            A completed poule match from the same tournament as this result container.

        Raises
        ------
        TypeError
            If match is not a PouleMatch.
        ValueError
            If match belongs to a different tournament or poule, or is incomplete.
        RuntimeError
            If a completed match does not have a valid winner index.
        """
        # Validate the given match
        if not isinstance(match, PouleMatch):
            raise TypeError(f'Match must be a PouleMatch object in PouleEntryResult._add_match_result() - got {type(match).__name__}')

        if match.tournament_id != self.tournament_id:
            raise ValueError(f'Match tournament ID {match.tournament_id} does not match PouleEntryResult tournament ID {self.tournament_id}.')

        if match.poule_id != self.poule_id:
            raise ValueError(f'Match poule ID {match.poule_id} does not match PouleEntryResult poule ID {self.poule_id}.')

        if match.is_incomplete():
            raise ValueError(f'Cannot add the incomplete match {match.id} to entry {self.entry.id}\'s poule results container.')
        
        # If this entry is not in the match, don't update the entry's results
        if not match.has_entry(self.entry):
            return
        
        # Identify whether this entry is entry 1 or 2
        entry_index = 0 if match.entry1 == self.entry else 1

        # Extract the winner index of the match
        winner_index = match.winner_index()

        if winner_index not in (0,1):
            raise RuntimeError(f'Completed poule match {match.id} has an invalid winner index of {winner_index} in PouleEntryResult._add_match_result().')

        # Add match result information
        self.num_matches += 1        
        self.num_victories += 1 if entry_index == winner_index else 0
        self.touches_scored += match.score1 if entry_index == 0 else match.score2
        self.touches_received += match.score2 if entry_index == 0 else match.score1


    # --- Helper Methods ---
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