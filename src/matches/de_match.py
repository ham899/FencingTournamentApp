from dataclasses import dataclass, field
from enum import Enum, auto

import validation
from entities.tournament_entry import TournamentEntry
from matches.tournament_match import TournamentMatch


class DEMatchResultType(Enum):
    """ Holds how a DE match was marked completed. """
    NORMAL = auto()
    BYE = auto()
    FORFEIT = auto()
    DOUBLE_FORFEIT = auto()


# kw_only=True allows tournament_id to be a required subclass field even though Match has inherited fields with defaults.
@dataclass(eq=False, kw_only=True)
class DEMatch(TournamentMatch):
    """
    Represents a DE match between two fencers in a tournament. Unlike a poule match, to initialize a match, an entry does not have to be present, 
    allowing for BYEs and empty matches in the tableau. Entry 1 represents the fencer on the top branch of a match in the tableau 
    and entry 2 represents the fencer on the bottom branch. This class is a subclass of the TournamentMatch class and inherits its attributes and methods. 
    Additionally, it has attributes to keep track of the round and match index within the round in the DE bracket.

    **Note:** Each present entry **must** have a **positive** DE seed. 
    However, this class does not validate whether the seed is structurally correct for this particular bracket position.

    Attributes
    ----------
    round_index : int
        The index of the round the DE match exists in, using zero-indexing.
    match_index : int
        The index of the match within the round as specified by the round_index, using zero-indexing.
        Note: The index for the parent match in the following round can be obtained by match_index // 2.

    score_to_win : int, default=15
        The score required to win the match. It defaults to 15 for DE matches but can be customized when setting up the tournament.
    """
    round_index: int
    match_index: int

    score_to_win: int = 15

    result_type: DEMatchResultType | None = field(default=None, init=False)
    
    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the DE match attributes (round index and match index), validates its inherited attributes, 
        **ensures** that the entries have DE seeds present, and marks the match as a BYE if only one entry is present.

        Initialization Cases:
            * Case 1: Both entries present \u2192 assumed to be a normal DE match.
            * Case 2: One None entry \u2192 assumed to be a BYE.
            * Case 3: Both entries are None \u2192 assumed to be an empty match.

        Raises
        ------
        TypeError
            If round index or match index is not an integer, or if an entry's DE seed is not an integer (**cannot** be None).
        ValueError
            If round index or match index is a negative integer, or if an entry's DE seed is not a positive integer.
        """
        # Validate DE match attributes
        validation.validate_non_negative_int(self.round_index, 'DE match round_index', 'DEMatch')
        validation.validate_non_negative_int(self.match_index, 'DE match match_index', 'DEMatch')

        # Get parent to validate common attributes
        super().__post_init__()

        # Require that both entries have DE seeds if they are present
        if self.entry1 is not None:
            validation.validate_positive_int(self.entry1.de_seed, f'Entry 1 DE seed for match {self.id}', 'DEMatch')
        if self.entry2 is not None:
            validation.validate_positive_int(self.entry2.de_seed, f'Entry 2 DE seed for match {self.id}', 'DEMatch')

        # Mark as a BYE if only one entry is provided
        if self.has_exactly_one_entry():
            self.mark_bye()

    # --- Properties ---
    @property
    def match_type(self) -> str:
        """Returns the type of match as a string."""
        return 'de'

    @property
    def next_match_index(self) -> int:
        """
        Returns the index the match would have in the following DE round. 
        The bracket should only use this value when a following round exists.
        """
        return self.match_index // 2

    # --- Predicate Methods ---
    def is_normal_result(self) -> bool:
        """Checks if the match result type is a normal result."""
        return self.result_type == DEMatchResultType.NORMAL

    def is_bye(self) -> bool:
        """Checks if the DE match is a BYE."""
        return self.result_type == DEMatchResultType.BYE
    
    def is_double_forfeit(self) -> bool:
        """Checks if the match was a double-forfeit."""
        return self.result_type == DEMatchResultType.DOUBLE_FORFEIT
    
    # --- Status Marking Methods ---
    def mark_bye(self) -> None:
        """Marks the DE match as a BYE."""
        if self.is_complete():
            raise ValueError(f'Cannot mark match {self.id} as a BYE since it is already complete.')
        
        if not self.has_exactly_one_entry():
            raise ValueError(f'Cannot mark match {self.id} as a BYE since it does not have exactly one entry.')

        self.score1 = None
        self.score2 = None
        self.forfeited_index = None
        self.result_type = DEMatchResultType.BYE
        self._mark_complete()
    
    def mark_double_forfeit(self) -> None:
        """Marks a match as a double-forfeit."""
        if self.is_complete():
            raise ValueError(f'Cannot mark match {self.id} as a double-forfeit since it is already complete.')
        
        if not self.has_both_entries():
            raise ValueError(f'Cannot mark match {self.id} as a double-forfeit unless both entries are present.')
        
        self.score1 = None
        self.score2 = None
        self.forfeited_index = None
        self.result_type = DEMatchResultType.DOUBLE_FORFEIT
        self._mark_complete()

    # --- Entry Mutation Methods ---
    def add_entry(self, entry: TournamentEntry, entry_index: int) -> None:
        """
        Adds an entry to the match at the given index and adds corresponding fencer information.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add to the match.
        entry_index : int
            The index to add the entry to: either 0 for entry 1 or 1 for entry 2.

        Note: This method **cannot** guarantee the entry's DE seed is valid for this specific match.

        Raises
        ------
        TypeError
            If the entry index is not an integer, or if the entry is not a TournamentEntry object.
        ValueError
            If the entry index is not 0 or 1 or if the entry's DE seed is not a positive integer.
        """
        if entry is None:
            raise TypeError(f'Cannot add a None entry to match {self.id}.')
        
        self._validate_entry_index(entry_index)
        self._validate_entry(entry, f'Entry {entry_index + 1}')
        
        self.set_entry(entry, entry_index)

    def add_entry1(self, entry: TournamentEntry) -> None:
        """Adds an entry to the match as entry 1."""
        self.add_entry(entry, 0)

    def add_entry2(self, entry: TournamentEntry) -> None:
        """Adds an entry to the match as entry 2."""
        self.add_entry(entry, 1)

    def remove_entry(self, entry_index: int) -> None:
        """
        Removes an entry from the match at the given index and removes fencer information.

        Parameters
        ----------
        entry_index : int
            The index to remove the entry from: either 0 for entry 1 or 1 for entry 2.

        Raises
        ------
        TypeError
            If the entry index is not an integer.
        ValueError
            If the entry index is not 0 or 1.
        """
        self._validate_entry_index(entry_index)
        self.set_entry(None, entry_index)

    def remove_entry1(self) -> None:
        """Removes the entry from the match at index 0 (entry 1)."""
        self.remove_entry(0)

    def remove_entry2(self) -> None:
        """Removes the entry from the match at index 1 (entry 2)."""
        self.remove_entry(1)

    # --- Score Record Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """Records a normal DE score result."""
        if self.is_bye():
            raise ValueError(f'Match {self.id} is a BYE and cannot have a score recorded. Reset it before recording a score.')

        if self.is_double_forfeit():
            raise ValueError(f'Match {self.id} already has a double-forfeit result. Reset it before recording a score.')
        
        super().record_score(score1, score2)

    # --- Result Query Methods ---
    def winner_entry(self) -> TournamentEntry | None:
        """
        Gets the entry object that is the winner of the match or returns None if there is no winner.
        
        Returns
        -------
        TournamentEntry | None
            The winning entry of the match, or None if there is no winner (e.g., a double-forfeit or an incomplete match).
    
        Raises
        ------
        RuntimeError
            If an impossible or impermissible state is detected.
        """
        # Case 1: Incomplete match
        if not self.is_complete():
            return None
        
        # Case 2: Normal match
        elif self.is_normal_result():
            if not self.has_both_entries():
                raise RuntimeError(f'Normal completed DE match {self.id} does not have both entries present.')
            
            winner_index = self.winner_index()

            if winner_index is None:
                raise RuntimeError(f'Normal completed DE match {self.id} has no winner index')

            return self.entry1 if winner_index == 0 else self.entry2

        # Case 3: BYE
        elif self.is_bye():
            if not self.has_exactly_one_entry():
                raise RuntimeError(f'Match {self.id} is marked as a BYE but does not have exactly one entry present.')
            
            return self.entry1 if self.entry1 is not None else self.entry2
            
        # Case 4: Forfeited match
        elif self.result_type is DEMatchResultType.FORFEIT:
            if not self.is_forfeit():
                raise RuntimeError(f'DE match {self.id} is marked as a forfeit but does not have a forfeited index.')

            forfeit_index = self._get_forfeit_index()

            return self.entry2 if forfeit_index == 0 else self.entry1
            
        # Case 5: Double-Forfeit match
        elif self.is_double_forfeit():
            if not self.has_both_entries():
                raise RuntimeError(f'The match {self.id} is marked as a double-forfeit but does not have both entries present.')
            
            return None # There is no winner as both entries forfeited
        
        # Case 6: Unrecognized result type
        raise RuntimeError(f'Completed DE match {self.id} has no recognized result type.')

    def loser_entry(self) -> TournamentEntry | tuple[TournamentEntry, TournamentEntry] | None:
        """
        Gets the loser(s) of the match as TournamentEntry objects or returns None if there is no loser.
        
        Returns
        -------
        TournamentEntry | tuple[TournamentEntry, TournamentEntry] | None
            The losing entry of the match, a tuple of both entries if it was a double-forfeit, or None if there is no loser (e.g., a BYE or an incomplete match
        
        Raises
        ------
        RuntimeError
            If an impossible or impermissible state is detected.
        """
        # Case 1: Incomplete match
        if not self.is_complete():
            return None
        
        # Case 2: Normal match
        if self.is_normal_result():
            if not self.has_both_entries():
                raise RuntimeError(f'Normal completed DE match {self.id} does not have both entries present.')
            
            loser_index = self.loser_index()
            
            if loser_index is None:
                raise RuntimeError(f'Normal completed DE match {self.id} has no loser index')
            
            return self.entry1 if loser_index == 0 else self.entry2

        # Case 3: BYE
        elif self.is_bye():
            if not self.has_exactly_one_entry():
                raise RuntimeError(f'Match {self.id} is marked as a BYE but does not have exactly one entry present.')

            return None # BYEs have no loser entry

        # Case 4: Forfeit
        elif self.result_type is DEMatchResultType.FORFEIT:
            if not self.is_forfeit():
                raise RuntimeError(f'DE match {self.id} is marked as a forfeit but does not have a forfeited index.')

            forfeit_index = self._get_forfeit_index()

            return self.entry1 if forfeit_index == 0 else self.entry2
        
        # Case 5: Double-forfeit
        elif self.is_double_forfeit():
            if not self.has_both_entries():
                raise RuntimeError(f'The match {self.id} is marked as a double-forfeit but does not have both entries present.')
            
            return (self.entry1, self.entry2) # Both are considered losers in a double-forfeit

        # Case 6: Unrecognized result type
        raise RuntimeError(f'Completed DE match {self.id} has no recognized result type.')

    # --- TournamentMatch Hook Implementations ---
    def _assign_normal_result_status(self) -> None:
        """Assigns subclass-specific normal result state."""
        self.result_type = DEMatchResultType.NORMAL

    def _assign_forfeit_status(self) -> None:
        """Assigns subclass-specific forfeit result state."""
        # No scores are necessary to be assigned for a DE forfeit
        self.score1 = None
        self.score2 = None

        # Assign result type as forfeit
        self.result_type = DEMatchResultType.FORFEIT

    def _clear_result_status(self) -> None:
        """A helper method to clear the result status of the match."""
        self.result_type = None

    # --- Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry | None, entry_name: str) -> None:
        """Validates that the entry is a TournamentEntry object and has a positive DE seed."""
        super()._validate_entry(entry, entry_name)
        if entry is not None:
            validation.validate_positive_int(entry.de_seed, f'{entry_name} DE seed for match {self.id}', 'DEMatch', '_validate_entry')

    def _get_forfeit_index(self) -> int:
        """A helper method to get the forfeited index of the match, ensuring it is valid."""
        if not self.has_both_entries():
            raise RuntimeError(
                f'DE match {self.id} is marked as a forfeit but does not have both entries present.'
            )

        if type(self.forfeited_index) is not int or self.forfeited_index not in (0, 1):
            raise RuntimeError(
                f'DE match {self.id} has an invalid forfeited index: {self.forfeited_index}.'
            )

        return self.forfeited_index

