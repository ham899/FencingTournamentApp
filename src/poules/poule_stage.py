from dataclasses import dataclass, field
from random import Random

import validation

from entities.tournament_entry import TournamentEntry
from poules.poule_round import PouleRound
from poules.results.poule_stage_results import PouleStageResults
from tournament.tournament_stage import TournamentStage


@dataclass(eq=False)
class PouleStage(TournamentStage):
    """
    Represent a tournament stage containing one or more rounds of poules.

    TournamentStage validates and sorts the initial seeded entries.
    The first round is then created in seed order during initialization.
    Subsequent rounds are created explicitly by calling ``advance_round()``,
    after all existing rounds are complete.

    Each subsequent round is seeded using aggregate results across all preceding rounds.
    Entries are ranked by victory ratio, indicator, and touches scored,
    with complete ties ordered using the stage's stored random seed.

    Results may only be recorded or replaced in the current round.
    To correct an earlier round, call ``rollback_to_round()`` to discard all
    subsequent rounds while preserving the selected round and its results.

    Parameters
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The participating entries and their initial seeds.
        Entries may be supplied in any order; they are stored in ascending seed order.
    num_rounds : int, default=1
        The number of poule rounds to conduct. Keyword-only.
    score_to_win : int | tuple[int, ...], default=5
        The target score for every round, or one target score per round
        in round-number order. Keyword-only.
    random_seed : int | None, default=None
        A nonnegative seed for ordering complete ranking ties.
        If None, a seed is generated and stored during initialization. Keyword-only.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The entries and their initial seeds.
        These seeded entries are stored in ascending seed order.
    num_rounds : int
        The total number of rounds to conduct in this stage.
    score_to_win : int | tuple[int, ...]
        The target score and maximum permitted recorded score for either entry in a match.
        A single integer applies to every round.
        A tuple supplies one value per round in round-number order.
    random_seed : int
        The seed used to order complete ranking ties.
    poule_rounds : list[PouleRound]
        The rounds created so far, in round-number order.
        Initially contains only round 1.
        Additional rounds are created as the stage progresses.
    """
    num_rounds: int = field(default=1, kw_only=True)
    score_to_win: int | tuple[int, ...] = field(default=5, kw_only=True)
    random_seed: int | None = field(default=None, kw_only=True)
    poule_rounds: list[PouleRound] = field(init=False, default_factory=list)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validate the stage configuration and create its first poule round.

        Call TournamentStage to validate and sort the initial seeded entries.
        Validate the number of rounds and target scores, 
        then generate and store a random seed if none was supplied. 
        Create round 1 from the initial seed order and its configured score to win.

        Raises
        ------
        TypeError
            If `stage_number` or `num_rounds` is not an integer,
            if `seeded_entries` is not a tuple, if an item is not a ``SeededEntry``,
            if an underlying entry is not a ``TournamentEntry``, if a seed is not an integer,
            if `score_to_win` is neither an integer nor a tuple of integers,
            or if `random_seed` is neither an integer nor None.
        ValueError
            If `stage_number` or `num_rounds` is not positive, if fewer than two entries are supplied,
            if the entries do not share a tournament ID, if an entry ID or fencer ID is repeated,
            if the seeds are not unique integers from 1 through the number of entries,
            if a ``score_to_win`` value is not positive, if the `score_to_win` tuple length differs from `num_rounds`,
            or if ``random_seed`` is negative.
        """
        location = 'PouleStage'

        # Validate the initialization parameters
        super().__post_init__()
        validation.validate_positive_int(self.num_rounds, 'num_rounds', location)
        self._validate_score_to_win(self.score_to_win)

        # Validate the random seed and assign one if none is provided
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', location)

        if self.random_seed is None:
            self.random_seed = Random().getrandbits(64)

        # Create the first round of the stage
        self.poule_rounds.append(self._create_first_round())


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying this poule stage."""
        return f'Poule stage with stage number {self.stage_number} in tournament {self.tournament_id}'

    @property
    def current_round_number(self) -> int:
        """Return the one-based number of the most recently created round."""
        return len(self.poule_rounds)

    @property
    def current_round_index(self) -> int:
        """Return the zero-based index of the most recently created round."""
        return self.current_round_number - 1

    @property
    def current_round(self) -> PouleRound:
        """
        Return the most recently created round.

        After the stage is complete, this remains the completed final round.
        """
        return self.poule_rounds[self.current_round_index]


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether another object represents the same poule stage.

        Poule stages are identified by their tournament ID and stage number.
        Configuration, entries, and match results are not compared.

        Parameters
        ----------
        other : object
            The object to compare with this stage.

        Returns
        -------
        bool
            True if other is a PouleStage with the same tournament ID and stage number; 
            otherwise, False.
        """
        if not isinstance(other, PouleStage):
            return False

        return (
            self.tournament_id == other.tournament_id and
            self.stage_number == other.stage_number
        )


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Return whether the first round in this stage has started."""
        return self.poule_rounds[0].has_started()

    def is_complete(self) -> bool:
        """Return whether all configured rounds have been created and completed."""
        return (
            len(self.poule_rounds) == self.num_rounds and
            all(poule_round.is_complete() for poule_round in self.poule_rounds)
        )


    # --- Round Access Methods ---
    def get_round_at(self, index: int) -> PouleRound:
        """
        Return the existing poule round at the specified index.

        Parameters
        ----------
        index : int
            The round's zero-based position within the stage.

        Returns
        -------
        PouleRound
            The round at the specified index.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the range from 0 through num_rounds - 1,
            or if the requested round has not yet been created.
        """
        self._validate_poule_round_index_for_accessing(index, 'get_round_at')
        return self.poule_rounds[index]


    # --- Match Result Recording Methods ---
    def record_match_score(self, round_index: int, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Record a scored result for a specified match in the current round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the stage.
            Must identify the current round.
        poule_index : int
            The poule's zero-based position within the round.
        match_index : int
            The match's zero-based position in the poule's scheduled bout order.
        score1 : int
            The score to record for entry 1.
        score2 : int
            The score to record for entry 2.

        Raises
        ------
        TypeError
            If any index or either score is not an integer.
        ValueError
            If any index is outside its valid range, if ``round_index`` does not identify the current round, 
            if the match is already complete, if either score is outside the permitted range, or if the scores are equal.
        """
        self._validate_poule_round_index_current_round(round_index, 'record_match_score')
        self.poule_rounds[round_index].record_match_score(poule_index, match_index, score1, score2)

    def record_forfeit(self, round_index:int , poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for a specified match in the current round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the stage.
            Must identify the current round.
        poule_index : int
            The poule's zero-based position within the round.
        match_index : int
            The match's zero-based position in the poule's scheduled bout order.
        forfeiting_index : int
            The index of the forfeiting entry: 0 for entry 1 and 1 for entry 2.

        Raises
        ------
        TypeError
            If any index is not an integer.
        ValueError
            If any round, poule, or match index is outside its valid range,
            if ``round_index`` does not identify the current round, 
            if ``forfeiting_index`` is neither 0 nor 1, or if the match is already complete.
        """
        self._validate_poule_round_index_current_round(round_index, 'record_forfeit')
        self.poule_rounds[round_index].record_forfeit(poule_index, match_index, forfeiting_index)

    def record_on_piste_match_score(self, round_index: int, poule_index: int, score1: int, score2: int) -> None:
        """
        Record a scored result for the on-piste match in a current-round poule.

        The on-piste match is the first incomplete match in the poule's scheduled bout order.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the stage.
            Must identify the current round.
        poule_index : int
            The poule's zero-based position within the round.
        score1 : int
            The score to record for entry 1.
        score2 : int
            The score to record for entry 2.

        Raises
        ------
        TypeError
            If either index or either score is not an integer.
        ValueError
            If either index is outside its valid range, if ``round_index`` does not identify the current round,
            if either score is outside the permitted range, or if the scores are equal.
        RuntimeError
            If the selected poule is complete and has no on-piste match.
        """
        self._validate_poule_round_index_current_round(round_index, 'record_on_piste_match_score')
        self.poule_rounds[round_index].record_on_piste_match_score(poule_index, score1, score2)


    # --- Result Replacement Methods ---
    def replace_with_score(self, round_index: int, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Replace a specified match's scored or forfeit result with new scores.

        Replacements are only permitted in the current round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the stage.
        poule_index : int
            The poule's zero-based position within the round.
        match_index : int
            The match's zero-based position in the poule's scheduled bout order.
        score1 : int
            The new score for entry 1.
        score2 : int
            The new score for entry 2.

        Raises
        ------
        TypeError
            If any index or either score is not an integer.
        ValueError
            If any index is outside its valid range, if the requested round has not been created, 
            if the round is not the current round, if the match is incomplete, 
            if either score is outside the permitted range, or if the scores are equal.
        """
        self._validate_poule_round_index_current_round(round_index, 'replace_with_score')
        self.poule_rounds[round_index].replace_with_score(poule_index, match_index, score1, score2)

    def replace_with_forfeit(self, round_index: int, poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Replace a specified match's scored or forfeit result with a forfeit.

        Replacements are permitted in the current round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the stage.
        poule_index : int
            The poule's zero-based position within the round.
        match_index : int
            The match's zero-based position in the poule's scheduled bout order.
        forfeiting_index : int
            The index of the forfeiting entry: 0 for entry 1 and 1 for entry 2.

        Raises
        ------
        TypeError
            If any index is not an integer.
        ValueError
            If any round, poule, or match index is outside its valid range, if the requested round has not been created, 
            if the round is not the current round, if forfeiting_index is neither 0 nor 1, or if the match is incomplete.
        """
        self._validate_poule_round_index_current_round(round_index, 'replace_with_forfeit')
        self.poule_rounds[round_index].replace_with_forfeit(poule_index, match_index, forfeiting_index)


    # --- Result Calculation Methods ---
    def calculate_results(self) -> PouleStageResults:
        """
        Calculate and return a snapshot of the stage's current results.

        Statistics are combined across all existing rounds using completed matches only. 
        The current round does not need to be complete.
        Complete ranking ties are ordered using the stage's stored random seed.

        Returns
        -------
        PouleStageResults
            A newly calculated snapshot of the aggregate stage results in descending ranking order.
        """
        return PouleStageResults(
            stage_number=self.stage_number, 
            poule_rounds=self.poule_rounds, 
            random_seed=self.random_seed
        )


    # --- Round Management Methods ---
    def advance_round(self) -> None:
        """
        Create the next round using the aggregate stage ranking.

        Use the configured target score for the new round.
        Existing rounds and their results are preserved.

        Raises
        ------
        RuntimeError
            If all configured rounds have already been created,
            or if any existing round is incomplete.
        """
        if len(self.poule_rounds) >= self.num_rounds:
            raise RuntimeError('All configured poule rounds have already been created')

        if not all(poule_round.is_complete() for poule_round in self.poule_rounds):
            raise RuntimeError('All existing poule rounds must be complete before advancing')

        next_round_index = len(self.poule_rounds)

        next_round = PouleRound(
            round_number=next_round_index + 1,
            stage_number=self.stage_number,
            entries=self._current_ranked_entries(),
            score_to_win=self._get_round_score_to_win(next_round_index)
        )

        self.poule_rounds.append(next_round)

    def rollback_to_round(self, round_index: int) -> None:
        """
        Discard all rounds after the specified round.

        Preserve the selected round and its results, making it the current round.
        Results in discarded rounds are lost.
        Selecting the current round leaves the stage unchanged.

        Parameters
        ----------
        round_index : int
            The zero-based index of the round to retain as the current round.

        Raises
        ------
        TypeError
            If ``round_index`` is not an integer.
        ValueError
            If ``round_index`` is outside the configured round range,
            or if the requested round has not yet been created.
        """
        self._validate_poule_round_index_for_accessing(round_index, 'rollback_to_round')

        # Remove all rounds after the specified round
        del self.poule_rounds[round_index + 1:]


    # --- Helper Methods ---
    def _get_round_score_to_win(self, round_index: int) -> int:
        """Return the configured score to win for the specified round."""
        if isinstance(self.score_to_win, tuple):
            return self.score_to_win[round_index]

        return self.score_to_win

    def _current_ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the entries in descending aggregate stage ranking order."""
        return self.calculate_results().ranked_entries

    def _create_first_round(self) -> PouleRound:
        """Create and return the first round using the stage's initial seed order."""
        entries: tuple[TournamentEntry, ...] = tuple(seed_entry.entry for seed_entry in self.seeded_entries)

        return PouleRound(
            round_number=1,
            stage_number=self.stage_number,
            entries=entries,
            score_to_win=self._get_round_score_to_win(0)
        )


    # --- Validation Helper Methods ---
    def _validate_poule_round_index(self, index: int, method_name: str) -> None:
        """
        Validate that an index falls within the stage's configured round range.

        This check does not require the specified round to have been created.

        Parameters
        ----------
        index : int
            The round's zero-based position within the stage.
        method_name : str
            The name of the method requesting validation, used in error messages.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the range from 0 through num_rounds - 1.
        """
        validation.validate_int_in_range(index, 0, self.num_rounds - 1, 'index', 'PouleStage', method_name)

    def _validate_poule_round_index_for_accessing(self, index: int, method_name: str) -> None:
        """
        Validate that an index identifies an existing round in this stage.

        Parameters
        ----------
        index : int
            The round's zero-based position within the stage.
        method_name : str
            The name of the method requesting validation, used in error messages.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the configured round range,
            or if the requested round has not yet been created.
        """
        self._validate_poule_round_index(index, method_name)
        current_round_index = self.current_round_index

        if index > current_round_index:
            raise ValueError(
                f'The round trying to be accessed does not currently exist yet - '
                f'index={index}, current round index={current_round_index}'
            )

    def _validate_poule_round_index_current_round(self, index: int, method_name: str) -> None:
        """
        Validate that an index identifies the current round for recording or replacing results.

        Match results may only be recorded or replaced in the most recently created round.
        Validation of the selected match is handled separately.

        Parameters
        ----------
        index : int
            The round's zero-based position within the stage.
        method_name : str
            The name of the method requesting validation, used in error messages.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the configured round range, 
            if the requested round has not yet been created,
            or if index does not identify the current round.
        """
        self._validate_poule_round_index_for_accessing(index, method_name)

        if index != self.current_round_index:
            raise ValueError('Recording or replacing can only be done in the current round')

    def _validate_score_to_win(self, score_to_win: int | tuple[int, ...]) -> None:
        """
        Validate the stage-wide or per-round scores to win.

        A single positive integer applies to every round. 
        A tuple must contain one positive integer for each configured round.

        Parameters
        ----------
        score_to_win : int | tuple[int, ...]
            The target score and maximum permitted recorded score for either entry in a match. 
            A tuple supplies values in round-number order.

        Raises
        ------
        TypeError
            If score_to_win is neither an integer nor a tuple, or if an item in the tuple is not an integer.
        ValueError
            If a score to win is not positive, or if the tuple length differs from num_rounds.
        """
        location = 'PouleStage'

        if not isinstance(score_to_win, (int, tuple)):
            raise TypeError(f'score_to_win must be either an int or a tuple of ints - got {type(score_to_win).__name__}')

        if isinstance(score_to_win, int):
            validation.validate_positive_int(score_to_win, 'score_to_win', location)

        else:
            if len(score_to_win) != self.num_rounds:
                raise ValueError(f'If score_to_win is a tuple, it must have the same length as num_rounds in {location}')

            for i, score in enumerate(score_to_win):
                validation.validate_positive_int(score, f'score_to_win value at index {i}', location)
