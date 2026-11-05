from dataclasses import dataclass

import validation


@dataclass(frozen=True, slots=True)
class DEConfig:
    """
    Store immutable settings for a direct elimination stage.

    Attributes
    ----------
    score_to_win : int
        The target score for matches in the stage.
    has_third_place_match : bool
        Whether to include a third-place match.
    use_consolation_bracket : bool
        Whether to include a consolation bracket.
    stop_at_round : int | None
        Round at which the bracket stops. Matches in this round are not played.
        None means the bracket runs to completion.

    Notes
    -----
    A stopped bracket cannot include a third-place match or a consolation bracket.
    """
    score_to_win: int
    has_third_place_match: bool
    use_consolation_bracket: bool
    stop_at_round: int | None


    def __post_init__(self) -> None:
        """
        Validate the stage settings and their compatibility.

        Raises
        ------
        TypeError
            If ``score_to_win`` is not an integer, 
            or if ``has_third_place_match`` or ``use_consolation_bracket`` is not a boolean, 
            or if ``stop_at_round`` is not an integer or None.
        ValueError
            If the target score or a provided stopping round is not positive,
            or a stopped bracket includes a third-place match or consolation bracket.
        """
        location = 'DEConfig'
        validation.validate_positive_int(self.score_to_win, 'Score to win', location)
        validation.validate_bool(self.has_third_place_match, 'Has third place match', location)
        validation.validate_bool(self.use_consolation_bracket, 'Use consolation bracket', location)
        validation.validate_optional_positive_int(self.stop_at_round, 'Stop at round', location)

        if self.stop_at_round is not None:
            if self.has_third_place_match:
                raise ValueError(f'A stopped bracket cannot have a third place match in {location}')

            if self.use_consolation_bracket:
                raise ValueError(f'A stopped bracket cannot have a consolation bracket in {location}')
