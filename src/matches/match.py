from dataclasses import dataclass, field
from enum import Enum, auto

import validation
from entities.fencer import Fencer


class MatchStatus(Enum):
    """
    Represents the current state of a match.
    
    Members
    -------
    NOT_STARTED
        The match has not yet begun.
    IN_PROGRESS
        The match is currently underway.
    COMPLETED
        The match has finished.
    """
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


@dataclass(eq=False)
class Match:
    """
    Represents a match between two fencers. It is the base class for all matches, and is meant to be a simple class with no forfeit methods.
    This class can be used to support isolated matches outside of a tournament context, and perhaps live match updating in the future.
    
    **Note:** a None fencer means this slot has no concrete fencer assigned yet.
    This can represent an anonymous practice fencer or a TBD tournament slot.

    Attributes
    ----------
    id : int
        The unique identifier of a match.
    
    score_to_win : int
        The maximum allowed score for either fencer and the conventional target score for the match.

        **Note:** Reaching this score does not automatically complete the match.

    fencer1 : Fencer | None, default=None
        The fencer in "position 1" in the match.
    
    fencer2 : Fencer | None, default=None
        The fencer in "position 2" in the match.

    score1: int | None, default=None
        The score of fencer 1.
    
    score2 : int | None, default=None
        The score of fencer 2.
    
    status : MatchStatus
        The status of the match.
    """
    id: int
    score_to_win: int

    fencer1: Fencer | None = field(default=None)
    fencer2: Fencer | None = field(default=None)

    score1: int | None = field(default=None, init=False)
    score2: int | None = field(default=None, init=False)

    status: MatchStatus = field(default=MatchStatus.NOT_STARTED, init=False)

    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the types and values of the match attributes after initialization.

        Raises
        ------
        TypeError
            If ID or score to win is not an integer or if a fencer is not either None or a Fencer object.
        ValueError
            If ID is negative, score to win is non-positive, or if fencer 1 and fencer 2 are the same.
        """
        # Validate ID and score to win
        validation.validate_positive_int(self.id, 'ID', 'Match')
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'Match')

        # Validate Fencers
        if self.fencer1 is not None and not isinstance(self.fencer1, Fencer):
            raise TypeError(f'Fencer 1 must be a Fencer or None - got {type(self.fencer1)}')
        if self.fencer2 is not None and not isinstance(self.fencer2, Fencer):
            raise TypeError(f'Fencer 2 must be a Fencer or None - got {type(self.fencer2)}')        
        if self.fencer1 is not None and self.fencer2 is not None and self.fencer1 == self.fencer2:
            raise ValueError(f'{self.fencer1} cannot be both fencer 1 and fencer 2 in a match; cannot fence yourself')

    # --- Properties ---
    @property
    def match_type(self) -> str:
        """Gets the type of match."""
        return 'standard'

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Determines whether two matches are equal based on type and match ID."""
        if type(other) is not type(self):
            return False
        return self.id == other.id
    
    # --- Predicate Methods ---
    def has_not_started(self) -> bool:
        """Returns true if the match has not been started; otherwise, returns false."""
        return self.status == MatchStatus.NOT_STARTED
    
    def is_in_progress(self) -> bool:
        """Returns true if the match is in progress; otherwise, returns false."""
        return self.status == MatchStatus.IN_PROGRESS

    def is_complete(self) -> bool:
        """
        Returns true if the match has been marked complete; otherwise, returns false. 
        
        **Note:** BYEs, forfeits, or double-forfeits are considered completed matches.
        """
        return self.status == MatchStatus.COMPLETED
    
    def is_incomplete(self) -> bool:
        """
        Returns true if the match has not been marked complete; otherwise, returns false. 
        
        **Note:** BYEs, forfeits, or double-forfeits are considered completed matches.
        """
        return not self.is_complete()

    def has_scores(self) -> bool:
        """Returns true if the match has scores recorded for both fencers; otherwise, returns false."""
        return self.score1 is not None and self.score2 is not None
    
    def is_tied(self) -> bool:
        """Returns true if the match is currently tied; otherwise, returns false."""
        return self.has_scores() and self.score1 == self.score2
    
    def has_both_fencers(self) -> bool:
        """Returns true if both fencer 1 and fencer 2 are present in the match; otherwise, returns false."""
        return self.fencer1 is not None and self.fencer2 is not None
    
    def has_reached_score_to_win(self) -> bool:
        """Returns true if either fencer has reached the score to win for the match; otherwise, returns false."""
        return self.has_scores() and (self.score1 >= self.score_to_win or self.score2 >= self.score_to_win)

    # --- State Transition Methods ---
    def start(self) -> None:
        """Starts a match: sets scores to zero and status to "in-progress". Can only start a match that has not started yet."""
        if not self.has_not_started():
            raise ValueError(f'Match {self.id} cannot be started because it has already been started.')
        self.score1 = 0
        self.score2 = 0
        self.status = MatchStatus.IN_PROGRESS

    def restart(self) -> None:
        """Restarts the match by resetting scores to zero and setting the status to in-progress."""
        self.score1 = 0
        self.score2 = 0
        self.status = MatchStatus.IN_PROGRESS

    def reset(self) -> None:
        """Resets the match to not started with no scores."""
        self.score1 = None
        self.score2 = None
        self.status = MatchStatus.NOT_STARTED

    def end(self) -> None:
        """
        Ends a live score-based match.

        Unlike mark_complete(), this requires the match to be in progress and to
        have a non-tied score.
        """
        self._require_in_progress()

        if self.is_tied():
            raise ValueError(f'Match {self.id} cannot be ended with a tie score of {self.score1}-{self.score2} - matches cannot end in ties.')

        self._mark_complete()

    # --- Live Score Update Methods ---
    def touch1(self) -> None:
        """Gives a point to fencer 1's score."""
        self._require_in_progress()

        if self.score1 >= self.score_to_win:
            raise ValueError(f'Fencer 1 already has the maximum score for match {self.id}.')

        self.score1 += 1

    def subtract1(self) -> None:
        """Takes a point away from fencer 1's score."""
        self._require_in_progress()

        if self.score1 <= 0:
            raise ValueError(f'Fencer 1 already has the minimum score of 0 for match {self.id}.')
            
        self.score1 -= 1

    def touch2(self) -> None:
        """Gives a point to fencer 2's score."""
        self._require_in_progress()

        if self.score2 >= self.score_to_win:
            raise ValueError(f'Fencer 2 already has the maximum score for match {self.id}.')

        self.score2 += 1

    def subtract2(self) -> None:
        """Takes a point away from fencer 2's score."""
        self._require_in_progress()

        if self.score2 <= 0:
            raise ValueError(f'Fencer 2 already has the minimum score of 0 for match {self.id}.')

        self.score2 -= 1

    def set_score(self, score1: int, score2: int) -> None:
        """
        Updates the live score without marking the match complete.
        
        Parameters
        ----------
        score1 : int
            The new score for fencer 1 in the match.
        score2 : int
            The new score for fencer 2 in the match.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If the match is not in progress, or if either score is negative
            or greater than the score to win.
        """
        self._require_in_progress()
        self._validate_score_values(score1, score2, allow_tie=True)
        self.score1 = score1
        self.score2 = score2

    # --- Score Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Records the result of a match by providing two scores: one for fencer 1 and one for fencer 2.
        The previous score values are overwritten and the match is marked complete.

        Parameters
        ----------
        score1 : int
            The score for fencer 1 in the match.
        score2 : int
            The score for fencer 2 in the match.
        
        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If either score is negative or greater than the score to win the match, or if the scores are equal (matches cannot end in a tie).
        """
        # Validate input scores
        self._validate_score_values(score1, score2, allow_tie=False)

        # Set score values and mark complete
        self.score1 = score1
        self.score2 = score2
        self._mark_complete()

    # --- Result Query Methods ---
    def score(self) -> tuple[int | None, int | None]:
        """Gets the current score of the match as a tuple of two integers, where the first integer is fencer 1's score and the second integer is fencer 2's score. If the scores are not set, returns None for the respective score."""
        return self.score1, self.score2
    
    def leader_index(self) -> int | None:
        """Returns the index of the leading fencer (0 for fencer 1, 1 for fencer 2) or None if the match is tied or not started."""
        if not self.has_scores() or self.score1 == self.score2:
            return None
        return 0 if self.score1 > self.score2 else 1

    def winner_index(self) -> int | None:
        """
        Gets the winner of the match as an index, 0 for fencer 1 and 1 for fencer 2, or returns None if there is no winner.

        Returns
        -------
        int | None
            The index of the winner of the match, where 0 corresponds to fencer 1 and 1 corresponds to fencer 2, or None if there is no winner.
            This method returns the winner for a simple match result and does not return if the scores are None.

        Raises
        ------
        ValueError
            If the match is a tie, which should not be possible in a match.
        """
        if self.is_incomplete() or not self.has_scores():
            return None
        
        if self.is_tied():
            raise RuntimeError('Completed matches cannot be tied.')

        winner_index = self.leader_index()

        if winner_index is None:
            raise ValueError('Completed matches must have a leader.')

        return winner_index

    def loser_index(self) -> int | None:
        """
        Gets the loser of the match as an index, 0 for fencer 1 and 1 for fencer 2, or returns None if there is no loser.

        Returns
        -------
        int | None
            The index of the loser of the match, where 0 corresponds to fencer 1 and 1 corresponds to fencer 2, or None if there is no loser.
            This method returns the loser for a simple match result and does not return if the scores are None.
            
        Raises
        ------
        ValueError
            If the match is a tie, which should not be possible in a match.
        """
        if self.is_incomplete() or not self.has_scores():
            return None
        
        if self.is_tied():
            raise RuntimeError('Completed matches cannot be tied.')

        leader_index = self.leader_index()

        if leader_index is None:
            raise ValueError('Completed matches must have a leader.')

        return 1 - leader_index

    def winner_fencer(self) -> Fencer | None:
        """
        Gets the fencer object that is the winner of the match if present.

        Returns
        -------
        Fencer | None
            The fencer object that is the winner of the match, or None if there is no winner fencer.
        """
        winner_index = self.winner_index()
        if winner_index == 0:
            return self.fencer1
        if winner_index == 1:
            return self.fencer2
        return None

    def loser_fencer(self) -> Fencer | None:
        """
        Gets the fencer object that is the loser of the match if present.

        Returns
        -------
        Fencer | None
            The fencer object that is the loser of the match, or None if there is no loser fencer.
        """
        loser_index = self.loser_index()
        if loser_index == 0:
            return self.fencer1
        if loser_index == 1:
            return self.fencer2
        return None

    # --- Helper Methods ---
    def _mark_complete(self) -> None:
        """
        Marks the match as complete after validating its internal score state.

        This helper supports normal score results and subclass-specific
        administrative results such as BYEs and forfeits. Callers are responsible
        for establishing any subclass-specific result state before or alongside
        completion.

        Raises
        ------
        ValueError
            If exactly one score is present, or if both scores are present and tied.
        """
        if (self.score1 is None) != (self.score2 is None):
            raise ValueError(f'Match {self.id} cannot be marked complete with only one score present - both scores must be present or both scores must be None.')

        if self.has_scores() and self.is_tied():
            raise ValueError(f'Match {self.id} cannot be marked complete with a tie score of {self.score1}-{self.score2} - matches cannot end in ties.')
        
        self.status = MatchStatus.COMPLETED

    def _validate_score_values(self, score1: int, score2: int, allow_tie: bool = True) -> None:
        """
        Validates the score values for a match.

        Parameters
        ----------
        score1 : int
            The score for fencer 1 in the match.
        score2 : int
            The score for fencer 2 in the match.
        allow_tie : bool, default=True
            Whether to allow the scores to be equal, 
            live matches can have equal scores, but completed matches cannot end in a tie.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If either score is negative or greater than the score to win the match, or if the scores are equal when allow_tie is False.
        """
        validation.validate_int_in_range(score1, 0, self.score_to_win, 'Score 1', 'Match', '_validate_score_values')
        validation.validate_int_in_range(score2, 0, self.score_to_win, 'Score 2', 'Match', '_validate_score_values')

        if not allow_tie and score1 == score2:
            raise ValueError(f'Score 1 and score 2 cannot be equal.')

    def _require_in_progress(self) -> None:
        """Raises a ValueError if the match is not in progress."""
        if not self.is_in_progress():
            raise ValueError(f'Match {self.id} must be in progress.')

        if not self.has_scores():
            raise ValueError(f'Match {self.id} must have initialized scores.')