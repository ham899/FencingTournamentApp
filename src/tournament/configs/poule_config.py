from dataclasses import dataclass

import validation


@dataclass(frozen=True, slots=True)
class PouleConfig:
    """
    Store immutable settings for a poule stage.

    Attributes
    ----------
    num_rounds : int
        The number of poule rounds in the stage.
    score_to_win : int | tuple[int, ...]
        The target score shared by all rounds, 
        or a tuple containing a target score per round in round order.
    """
    num_rounds: int
    score_to_win: int | tuple[int, ...]


    def __post_init__(self) -> None:
        """
        Validate the round count and target scores.

        Raises
        ------
        TypeError
            If the number of rounds is not an integer, if the target score is not either an integer or tuple, 
            or if the target score is a tuple but does not contain only integers.
        ValueError
            If the number of rounds or any target score is not positive,
            or a target-score tuple does not contain one score per round.
        """
        location = 'PouleConfig'

        validation.validate_positive_int(self.num_rounds, 'Number of rounds', location)

        if type(self.score_to_win) is not int and not isinstance(self.score_to_win, tuple):
            raise TypeError(f'score_to_win must be an int or tuple in {location} - got {type(self.score_to_win).__name__}')

        if type(self.score_to_win) is int:
            validation.validate_positive_int(self.score_to_win, 'score_to_win', location)

        else:
            if len(self.score_to_win) != self.num_rounds:
                raise ValueError(
                    f'score_to_win must contain one score per round in {location} '
                    f'- expected {self.num_rounds}, got {len(self.score_to_win)}'
                )

            for i, score in enumerate(self.score_to_win):
                validation.validate_positive_int(score, f'Score to win at index {i}', location)
