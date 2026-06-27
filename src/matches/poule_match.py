from dataclasses import dataclass, field
from enum import Enum, auto

import validation
from entities.tournament_entry import TournamentEntry
from matches.tournament_match import TournamentMatch


class PouleMatchResultType(Enum):
    """
    Represents how a match was marked complete for a poule match.

    Members
    -------
    NORMAL
        The match was marked complete by recording a normal score.
    FORFEIT
        The match was marked complete by recording a forfeit.
    """
    NORMAL = auto()
    FORFEIT = auto()


# kw_only=True allows tournament_id to be a required subclass field even though Match has inherited fields with defaults.
@dataclass(eq=False, kw_only=True)
class PouleMatch(TournamentMatch):
    """
    Represents a poule match between two entries in a tournament.
    This class is a subclass of the TournamentMatch class and inherits its attributes and methods.
    Both entries **must** be present for a poule match to be valid.
    Let entry 1 represent the fencer on the right of the referee and entry 2 represent the fencer on the left.

    Attributes
    ----------
    poule_id: int
        The unique identifier for the poule that the match belongs to.
    match_index: int
        The index of the match within the poule, using zero-indexing.

    score_to_win: int, default=5
        The score required to win the match. It defaults to 5 for poule matches but can be customized when setting up the tournament.
    
    result_type: PouleMatchResultType, default=None
        How the match was marked complete.
    """
    poule_id: int
    match_index: int

    score_to_win: int = 5

    result_type: PouleMatchResultType | None = field(default=None, init=False)

    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the poule match attributes - poule ID and match index, 
        validates the inherited attributes, and checks that both entries are present for the poule match.

        Raises
        ------
        TypeError
            If poule ID or match index is not an integer.
        ValueError
            If the poule ID is not positive, if the match index is negative, or if there is a None entry.
        """
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleMatch')
        validation.validate_non_negative_int(self.match_index, 'Match index', 'PouleMatch')
        
        # Validate inherited attributes and use poule match validation rules
        super().__post_init__()

    # --- Properties ---
    @property
    def match_type(self) -> str:
        """Returns the match type as a string."""
        return 'poule'

    # --- Predicate methods ---
    def is_normal_result(self) -> bool:
        """Checks if the match result type is a normal result."""
        return self.result_type == PouleMatchResultType.NORMAL
    
    # --- Result Query Methods ---
    def winner_entry(self) -> TournamentEntry | None:
        """
        Gets the winner entry of the match if there is a winner.

        Returns
        -------
        TournamentEntry | None
            Returns the tournament entry object that is the winner of the match or None if there is no winner.
        """
        # Case 1: Incomplete Match
        if self.is_incomplete():
            return None
        
        # Case 2: Normal match
        elif self.is_normal_result():
            if not self.has_both_entries():
                raise RuntimeError(f'Normal completed poule match {self.id} does not have both entries.')
            
            winner_index = self.winner_index()
            
            if winner_index is None:
                raise RuntimeError(f'A normal completed match {self.id} has no winner index.')
            
            return self.entry1 if winner_index == 0 else self.entry2

        # Case 3: Forfeited match
        elif self.result_type is PouleMatchResultType.FORFEIT:
            if not self.is_forfeit():
                raise RuntimeError(f'Poule match {self.id} is marked as a forfeit result but has no forfeited index.')

            if not self.has_both_entries():
                raise RuntimeError(f'The match {self.id} is marked as a forfeit but does not have both entries present.')

            forfeit_index = self.forfeited_index

            if forfeit_index is None:
                raise RuntimeError(f'Match {self.id} is marked as a forfeit without a forfeited index.')
            
            if type(forfeit_index) is not int or forfeit_index not in (0, 1):
                raise RuntimeError(f'Match {self.id} is marked as a forfeit with an invalid forfeited index: {forfeit_index}.')

            return self.entry2 if forfeit_index == 0 else self.entry1
        
        # Case 4: Unrecognized result type
        else:
            raise RuntimeError(f'Completed poule match {self.id} has no recognized result type.')

    def loser_entry(self) -> TournamentEntry | None:
        """
        Gets the loser of a match or None if there is no loser.

        Returns
        -------
        TournamentEntry | None
            Returns the tournament entry object that is the loser of the match or None if there is no loser.
        """
        # Case 1: Incomplete match
        if self.is_incomplete():
            return None
        
        # Case 2: Normal match
        elif self.is_normal_result():
            if not self.has_both_entries():
                raise RuntimeError(f'Normal completed poule match {self.id} does not have both entries.')
            
            loser_index = self.loser_index()
            
            if loser_index is None:
                raise RuntimeError(f'A normal completed match {self.id} has no loser index.')
            
            return self.entry1 if loser_index == 0 else self.entry2

        # Case 3: Forfeited match
        elif self.result_type is PouleMatchResultType.FORFEIT:
            if not self.is_forfeit():
                raise RuntimeError(f'Poule match {self.id} is marked as a forfeit result but has no forfeited index.')

            if not self.has_both_entries():
                raise RuntimeError(f'The match {self.id} is marked as a forfeit but does not have both entries present.')

            forfeit_index = self.forfeited_index
            
            if forfeit_index is None:
                raise RuntimeError(f'Match {self.id} is marked as a forfeit without a forfeited index.')
            
            if type(forfeit_index) is not int or forfeit_index not in (0, 1):
                raise RuntimeError(f'Match {self.id} is marked as a forfeit with an invalid forfeited index: {forfeit_index}.')
            
            return self.entry1 if forfeit_index == 0 else self.entry2
        
        # Case 4: Unrecognized result type
        else:
            raise RuntimeError(f'Completed poule match {self.id} has no recognized result type.')

    # --- TournamentMatch Hook Implementations ---
    def _assign_normal_result_status(self) -> None:
        """Assigns subclass-specific normal result state."""
        self.result_type = PouleMatchResultType.NORMAL

    def _assign_forfeit_status(self) -> None:
        """Assigns subclass-specific forfeit result state."""
        # Set score so the winner gets the maximum number of points and the loser gets 0 points
        if self.forfeited_index == 0:
            self.score1 = 0
            self.score2 = self.score_to_win
        elif self.forfeited_index == 1:
            self.score1 = self.score_to_win
            self.score2 = 0
        else:
            raise RuntimeError(f'Poule match {self.id} cannot assign a forfeit score without a valid forfeited index.')

        # Assign result type as forfeit
        self.result_type = PouleMatchResultType.FORFEIT

    def _clear_result_status(self) -> None:
        """A helper method to clear the result status of the match."""
        self.result_type = None

    # --- Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry | None, entry_name: str) -> None:
        """A helper method to validate an entry for a poule match; poule matches require both entries to be present."""
        if entry is None:
            raise ValueError(f'{entry_name} cannot be None for a poule match.')
        super()._validate_entry(entry, entry_name)