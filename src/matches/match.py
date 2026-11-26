from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import validation

from entities import Weapon


@dataclass(eq=False)
class Match(ABC):
    """
    Represent the shared scoring and completion behaviour of a fencing match.

    Concrete subclasses provide the match type, descriptive label, and weapon.
    They may also define participants, identifiers, and result types specific to their context.

    A match begins incomplete with both scores set to ``None``. 
    Recording a valid pair of unequal scores completes the match. 
    Subclasses may also record a scoreless result, such as a forfeit.

    Attributes
    ----------
    score_to_win : int
        Maximum permitted score for either fencer. In a scored sabre match,
        the winner must reach this target. A foil or epee match may finish
        with a winning score below the target.
    score1 : int | None, default=None
        Recorded score of fencer 1, or ``None`` when the match has no scores.
    score2 : int | None, default=None
        Recorded score of fencer 2, or ``None`` when the match has no scores.
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
    def label(self) -> str:
        """Return a descriptive label identifying the match."""
        pass

    @property
    @abstractmethod
    def match_type(self) -> str:
        """Return a string identifying the concrete type of match."""
        pass

    @property
    @abstractmethod
    def weapon(self) -> Weapon:
        """Return the weapon used in the match."""
        pass

    @property
    def score(self) -> tuple[int | None, int | None]:
        """
        Return the recorded scores as ``(score1, score2)``.

        An incomplete match or a completed scoreless result returns ``(None, None)``.
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

        Raises
        ------
        ValueError
            If the match has no recorded result to reset.
        """
        if self.is_incomplete():
            raise ValueError(f'Cannot reset {self.label} because it has no recorded result')

        self.score1 = None
        self.score2 = None
        self._completed = False


    # --- Score Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Record a scored result and mark the match complete.

        Cannot record a match score if the match is already complete - 
        use `replace_with_score` instead.

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
            If the match is already complete, either score is outside the permitted range, 
            the scores are tied, or the winning sabre score is below ``score_to_win``.
        """
        if self.is_complete():
            raise ValueError(
                f'Cannot record a score for {self.label} because the match is already complete '
                '- use replace_with_score() instead'
            )

        self._validate_score_values(score1, score2, 'record_score')

        self.score1, self.score2 = score1, score2

        self._mark_complete()

    def replace_with_score(self, score1: int, score2: int) -> None:
        """
        Replace a previously recorded match result with new scores.

        Parameters
        ----------
        score1 : int
            The new score for fencer 1.
        score2 : int
            The new score for fencer 2.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If the match is incomplete, either score is outside the permitted range, 
            the scores are tied, or the winning sabre score is below ``score_to_win``.
        """
        if self.is_incomplete():
            raise ValueError(
                f'Cannot replace the score for {self.label} because no result has been recorded - '
                'use record_score() instead'
            )

        self._validate_score_values(score1, score2, 'replace_with_score')

        self.score1, self.score2 = score1, score2


    # --- Validation Helper Methods ---
    def _validate_score_values(self, score1: int, score2: int, method_name: str) -> None:
        """
        Validate a pair of scores as a completed match result.

        Parameters
        ----------
        score1 : int
            The proposed score of fencer 1.
        score2 : int
            The proposed score of fencer 2.
        method_name : str
            The name of the caller method where the scores are being validated.

        Raises
        ------
        TypeError
            If either score is not an integer or ``method_name`` is not a string.
        ValueError
            If either score is outside the inclusive range from zero to ``score_to_win``,
            the scores are tied, or the winning sabre score is below ``score_to_win``.
        """
        validation.validate_string(method_name, 'Method name', self.__class__.__name__, '_validate_score_values')

        validation.validate_int_in_range(score1, 0, self.score_to_win, 'Score 1', 'Match', method_name)
        validation.validate_int_in_range(score2, 0, self.score_to_win, 'Score 2', 'Match', method_name)

        if score1 == score2:
            raise ValueError(f'Score 1 and score 2 cannot be equal in {self.label}')

        if self.weapon == Weapon.SABRE:
            if max(score1, score2) != self.score_to_win:
                raise ValueError(
                    f'A sabre match must reach the score to win of {self.score_to_win} touches'
                )


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
            If exactly one score is present, 
            or if both scores are present and violate the scoring rules for the match weapon.
        """
        score1, score2 = self.score

        if (score1 is None) != (score2 is None):
            raise ValueError(
                f'{self.label} cannot be marked complete with only one score present - '
                'both scores must be present or both scores must be None'
            )

        if score1 is not None and score2 is not None:
            self._validate_score_values(score1, score2, '_mark_complete')

        self._completed = True
