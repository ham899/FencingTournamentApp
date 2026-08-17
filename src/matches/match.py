from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import validation


@dataclass(eq=False)
class Match(ABC):
    """
    Represents the shared scoring and completion behaviour of a fencing match.

    ``Match`` is an abstract base class and cannot be instantiated directly.
    Concrete subclasses must provide a match type and a descriptive label.
    They may also add participants, identifiers, and result types appropriate
    to their context.

    A match begins incomplete with no recorded scores. It can be completed by
    recording a valid, non-tied score or by a subclass recording a scoreless
    result, such as a forfeit.

    Attributes
    ----------
    score_to_win : int
        The conventional target score and the maximum permitted 
        recorded score for either fencer.
    score1 : int | None, default=None
        The recorded score of fencer 1, or ``None`` if no score is recorded.
    score2 : int | None, default=None
        The recorded score of fencer 2, or ``None`` if no score is recorded.
    _completed : bool, default=False
        Whether the match has been marked complete.
    """
    score_to_win: int

    score1: int | None = field(default=None, init=False)
    score2: int | None = field(default=None, init=False)

    _completed: bool = field(default=False, init=False, repr=False)


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the match configuration after initialization.

        Raises
        ------
        TypeError
            If ``score_to_win`` is not an integer.
        ValueError
            If ``score_to_win`` is not positive.
        """
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'Match')


    # --- Properties ---
    @property
    @abstractmethod
    def match_type(self) -> str:
        """Return a string identifying the concrete type of match."""
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        """Return a descriptive label identifying the match."""
        pass

    @property
    def score(self) -> tuple[int | None, int | None]:
        """
        Return the current score as ``(score1, score2)``.

        Either value may be ``None`` when the match has no recorded score.
        """
        return self.score1, self.score2
    
    @property
    def winner_index(self) -> int | None:
        """
        Return the index of the winner indicated by the recorded scores.

        The winner is determined only for a completed match with two recorded
        scores. A completed scoreless result, such as a forfeit, cannot be
        interpreted by this base class.

        Returns
        -------
        int | None
            ``0`` if fencer 1 won, ``1`` if fencer 2 won, or ``None`` if the
            match is incomplete or does not have two recorded scores.

        Raises
        ------
        RuntimeError
            If the completed match has tied scores.
        """
        if self.is_incomplete():
            return None
        
        score1, score2 = self.score

        if score1 is None or score2 is None:
            return None
        
        if score1 == score2:
            raise RuntimeError(f'{self.label} is complete but has tied scores')

        return 0 if score1 > score2 else 1

    @property    
    def loser_index(self) -> int | None:
        """
        Return the index of the loser indicated by the recorded scores.

        The loser is determined only for a completed match with two recorded
        scores. A completed scoreless result, such as a forfeit, cannot be
        interpreted by this base class.

        Returns
        -------
        int | None
            ``0`` if fencer 1 lost, ``1`` if fencer 2 lost, or ``None`` if the
            match is incomplete or does not have two recorded scores.

        Raises
        ------
        RuntimeError
            If the completed match has tied scores.
        """
        if self.is_incomplete():
            return None

        score1, score2 = self.score

        if score1 is None or score2 is None:
            return None
        
        if score1 == score2:
            raise RuntimeError(f'{self.label} is complete but has tied scores')

        return 0 if score1 < score2 else 1
    
    
    # --- Predicate Methods ---
    def is_complete(self) -> bool:
        """
        Return whether the match has been marked complete.

        A completed match may contain a recorded score or represent a scoreless result such as a forfeit.
        """
        return self._completed
    
    def is_incomplete(self) -> bool:
        """
        Return whether the match has not been marked complete.

        This is the logical inverse of :meth:`is_complete`.
        """
        return not self.is_complete()


    # --- State Change Methods ---
    def reset(self) -> None:
        """
        Reset the match to its initial incomplete state.

        Both recorded scores are cleared and the completion state is set to ``False``.
        """
        self.score1 = None
        self.score2 = None
        
        self._completed = False


    # --- Score Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Record a scored result and mark the match complete.

        Any previously recorded scores are overwritten. The scores must be within 
        the inclusive range from zero to ``score_to_win`` and cannot be equal.

        Parameters
        ----------
        score1 : int
            The final score of fencer 1.
        score2 : int
            The final score of fencer 2.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If either score is outside the permitted range or if the scores are equal.
        """
        self._validate_score_values(score1, score2)

        self.score1 = score1
        self.score2 = score2
        
        self._mark_complete()


    # --- Validation Helper Methods ---
    def _validate_score_values(self, score1: int, score2: int) -> None:
        """
        Validate a pair of scores as a completed match result.

        Parameters
        ----------
        score1 : int
            The proposed score of fencer 1.
        score2 : int
            The proposed score of fencer 2.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If either score is outside the inclusive range from zero to
            ``score_to_win`` or if the scores are equal.
        """
        validation.validate_int_in_range(score1, 0, self.score_to_win, 'Score 1', 'Match', '_validate_score_values')
        validation.validate_int_in_range(score2, 0, self.score_to_win, 'Score 2', 'Match', '_validate_score_values')

        if score1 == score2:
            raise ValueError(f'Score 1 and score 2 cannot be equal in {self.label}')


    # --- State Change Helper Methods ---
    def _mark_complete(self) -> None:
        """
        Validate the internal score state and mark the match complete.

        A match may be completed with two valid, non-tied scores or with both
        scores absent. Allowing both scores to be absent supports scoreless
        results recorded by subclasses, such as forfeits.

        Raises
        ------
        TypeError
            If both scores are present and either score is not an integer.
        ValueError
            If exactly one score is present, if either present score is
            outside the permitted range, or if the scores are tied.
        """
        score1, score2 = self.score

        if (score1 is None) != (score2 is None):
            raise ValueError(f'{self.label} cannot be marked complete with only one score present - '
                             'both scores must be present or both scores must be None')

        if score1 is not None and score2 is not None:
            self._validate_score_values(score1, score2)

        self._completed = True
