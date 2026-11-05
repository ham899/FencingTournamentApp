from dataclasses import dataclass, field
from random import Random

import validation

from entities.seeded_entry import SeededEntry
from entities.tournament_entry import TournamentEntry
from poules.poule_round import PouleRound
from poules.results.poule_stage_results import PouleStageResults


@dataclass(eq=False)
class PouleStage():
    """
    Represents a tournament stage containing one or more rounds of poules.

    The first round is created during initialization using the supplied entry seeds. 
    Subsequent rounds are created automatically when results recorded through this stage complete the current round, 
    until the configured number of rounds has been reached.

    Each subsequent round is seeded using the aggregate results across all preceding rounds. 
    Entries are ranked by victory ratio, indicator, and touches scored, with complete ties ordered using the stage's stored random seed.

    Results may be replaced in the current round, 
    or in the immediately preceding round before the current round has started. 
    Replacing a result in the preceding round regenerates the unstarted current round using the updated aggregate ranking.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The entries and their initial seeds. 
        These seeded entries will be stored in ascending seed order.
    num_rounds : int, default=1
        The total number of rounds to conduct in this stage.
    score_to_win : int | tuple[int, ...], default=5
        The target score and maximum permitted recorded score for either entry in a match. 
        A single integer applies to every round.
        A tuple supplies one value per round in round-number order.
    random_seed : int | None, default=None
        A nonnegative seed used to order complete ranking ties.
        If None is supplied, an integer seed is generated and stored during initialization.
    poule_rounds : list[PouleRound]
        The rounds created so far, in round-number order.
        Initially contains only round 1. 
        Additional rounds are created as the stage progresses.
    """
    stage_number: int
    seeded_entries: tuple[SeededEntry, ...]

    num_rounds: int = 1
    score_to_win: int | tuple[int, ...] = field(default=5, kw_only=True)
    random_seed: int | None = field(default=None, kw_only=True)
    poule_rounds: list[PouleRound] = field(init=False, default_factory=list)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validate the stage configuration and create its first poule round.

        Sort the supplied entries into ascending seed order. 
        If no random seed is supplied, generate and store one for subsequent stage result calculations. 
        Create round 1 using the initial seed order and its configured score to win.

        Raises
        ------
        TypeError
            If stage_number or num_rounds is not an integer,
            if seeded_entries is not a tuple, if an item is not a ``SeededEntry``, 
            if an underlying entry is not a ``TournamentEntry``, if a seed is not an integer, 
            if score_to_win is neither an integer nor a tuple of integers, 
            or if random_seed is neither an integer nor None.
        ValueError
            If stage_number or num_rounds is not positive, if fewer than two entries are supplied, 
            if the entries do not share a tournament ID, if an entry ID is repeated,
            if the seeds are not exactly the integers from 1 through the number of entries, 
            if a ``score_to_win`` value is not positive, if the score_to_win tuple length differs from num_rounds, 
            or if ``random_seed`` is negative.
        """
        location = 'PouleStage'

        # Validate the initialization parameters
        validation.validate_positive_int(self.stage_number, 'stage_number', location)
        self._validate_seeded_entries(self.seeded_entries)
        validation.validate_positive_int(self.num_rounds, 'num_rounds', location)
        self._validate_score_to_win(self.score_to_win)

        # Sort the seeded entries by seed in ascending order
        self.seeded_entries = self._sort_seeded_entries(self.seeded_entries)

        # Validate the random seed and assign one if none is provided
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', location)

        if self.random_seed is None:
            self.random_seed = Random().getrandbits(64)

        # Create the first round of the stage
        self.poule_rounds.append(self._create_first_round())


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the entries in this stage."""
        return self.seeded_entries[0].entry.tournament_id

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

    def is_incomplete(self) -> bool:
        """Return whether any configured round has yet to be created or completed."""
        return not self.is_complete()


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

        If this completes the round and additional rounds are configured,
        create the next round using the aggregate stage ranking.

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
        self._validate_poule_round_index_for_recording(round_index, 'record_match_score')
        self.poule_rounds[round_index].record_match_score(poule_index, match_index, score1, score2)
        self._create_next_round_if_needed()

    def record_forfeit(self, round_index:int , poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for a specified match in the current round.

        If this completes the round and additional rounds are configured,
        create the next round using the aggregate stage ranking.

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
        self._validate_poule_round_index_for_recording(round_index, 'record_forfeit')
        self.poule_rounds[round_index].record_forfeit(poule_index, match_index, forfeiting_index)
        self._create_next_round_if_needed()

    def record_on_piste_match_score(self, round_index: int, poule_index: int, score1: int, score2: int) -> None:
        """
        Record a scored result for the on-piste match in a current-round poule.

        The on-piste match is the first incomplete match in the poule's scheduled bout order. 
        If recording its result completes the round and additional rounds are configured, 
        create the next round using the aggregate stage ranking.

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
        self._validate_poule_round_index_for_recording(round_index, 'record_on_piste_match_score')
        self.poule_rounds[round_index].record_on_piste_match_score(poule_index, score1, score2)
        self._create_next_round_if_needed()


    # --- Result Replacement Methods ---
    def replace_with_score(self, round_index: int, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Replace a specified match's scored or forfeit result with new scores.

        Replacements are permitted in the current round, 
        or in the immediately preceding round before the current round has started.

        Replacing a result in the preceding round removes and regenerates the unstarted current 
        round using the updated aggregate stage ranking and the stage's stored random seed.

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
            if the round is neither the current round nor the immediately preceding round with an unstarted current round, 
            if the match is incomplete, if either score is outside the permitted range, or if the scores are equal.
        """
        self._validate_poule_round_index_for_replacing(round_index, 'replace_with_score')
        self.poule_rounds[round_index].replace_with_score(poule_index, match_index, score1, score2)
        self._adjust_rounds_for_replacement(round_index)

    def replace_with_forfeit(self, round_index: int, poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Replace a specified match's scored or forfeit result with a forfeit.

        Replacements are permitted in the current round, 
        or in the immediately preceding round before the current round has started.

        Replacing a result in the preceding round removes and regenerates the unstarted current 
        round using the updated aggregate stage ranking and the stage's stored random seed.

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
            if the round is neither the current round nor the immediately preceding round with an unstarted current round, 
            if forfeiting_index is neither 0 nor 1, or if the match is incomplete.
        """
        self._validate_poule_round_index_for_replacing(round_index, 'replace_with_forfeit')
        self.poule_rounds[round_index].replace_with_forfeit(poule_index, match_index, forfeiting_index)
        self._adjust_rounds_for_replacement(round_index)


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


    # --- Helper Methods ---
    def _get_round_score_to_win(self, round_index: int) -> int:
        """Return the configured score to win for the specified round."""
        if isinstance(self.score_to_win, tuple):
            return self.score_to_win[round_index]

        return self.score_to_win

    def _sort_seeded_entries(self, seeded_entries: tuple[SeededEntry, ...]) -> tuple[SeededEntry, ...]:
        """Return the supplied seeded entries in ascending seed order."""
        return tuple(sorted(seeded_entries, key=lambda entry: entry.seed))

    def _current_stage_results_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the entries in descending aggregate stage ranking order."""
        return self.calculate_results().stage_results_entries

    def _create_first_round(self) -> PouleRound:
        """Create and return the first round using the stage's initial seed order."""
        entries: tuple[TournamentEntry, ...] = tuple(seed_entry.entry for seed_entry in self.seeded_entries)

        return PouleRound(
            round_number=1,
            stage_number=self.stage_number,
            entries=entries,
            score_to_win=self._get_round_score_to_win(0)
        )

    def _create_next_round_if_needed(self) -> None:
        """
        Append the next round if all existing rounds are complete and more are configured.

        Seed its entries using the aggregate stage ranking.
        """
        if len(self.poule_rounds) < self.num_rounds:
            if all(poule_round.is_complete() for poule_round in self.poule_rounds):
                next_round_number = len(self.poule_rounds) + 1

                entries = self._current_stage_results_entries()

                next_round = PouleRound(
                    round_number=next_round_number,
                    stage_number=self.stage_number,
                    entries=entries,
                    score_to_win=self._get_round_score_to_win(next_round_number - 1)
                )

                self.poule_rounds.append(next_round)

    def _adjust_rounds_for_replacement(self, index: int) -> None:
        """
        Regenerate the unstarted current round if the preceding round was corrected.

        Otherwise, create the next round only if needed.
        """
        if index == self.current_round_index - 1:
            if not self.poule_rounds[self.current_round_index].has_started():
                self.poule_rounds.pop()

        self._create_next_round_if_needed()


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

    def _validate_poule_round_index_for_recording(self, index: int, method_name: str) -> None:
        """
        Validate that an index identifies the current round for result recording.

        New match results may only be recorded in the most recently created round. 
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
            If index is outside the configured round range, if the requested round has not yet been created,
            or if index does not identify the current round.
        """
        self._validate_poule_round_index_for_accessing(index, method_name)

        if index != self.current_round_index:
            raise ValueError('Only results can be recorded for the current round')

    def _validate_poule_round_index_for_replacing(self, index: int, method_name: str) -> None:
        """
        Validate that an index identifies a round eligible for result replacement.

        Replacements are permitted in the current round, 
        or in the immediately preceding round before the current round has started. 
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
            If index is outside the configured round range, if the requested round has not yet been created,
            if index identifies a round earlier than the immediately preceding round, 
            or if index identifies the preceding round after the current round has started.
        """
        self._validate_poule_round_index_for_accessing(index, method_name)

        current_round_index = self.current_round_index

        if index == current_round_index:
            return

        if index == current_round_index - 1 and not self.poule_rounds[current_round_index].has_started():
            return

        raise ValueError(
            'Results can only be replaced in the current round, '
            'or in the previous round before the current round has started'
        )

    def _validate_entries(self, entries: tuple[TournamentEntry, ...], method_name: str | None = None) -> None:
        """
        Validate entry types, minimum count, tournament membership, and uniqueness.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The tournament entries to validate.
        method_name : str | None, optional
            The name of the method requesting validation.
            If None, only the class name is used in error messages.

        Raises
        ------
        TypeError
            If method_name is neither a string nor None, if entries is not a tuple,
            or if an item is not a TournamentEntry.
        ValueError
            If fewer than two entries are supplied, 
            if an entry's tournament ID differs from the stage's tournament ID,
            or if an entry ID occurs more than once.
        """
        # Validate location input
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in PouleStage._validate_entries() - got {type(method_name).__name__}')

        location = 'PouleStage' if method_name is None else f'PouleStage.{method_name}()'

        # Validate entries
        if not isinstance(entries, tuple):
            raise TypeError(f'Entries must be a tuple in {location} - got {type(entries).__name__}')

        if len(entries) < 2:
            raise ValueError(f'Entries must contain at least 2 entries in {location} - got {len(entries)}')

        # Validate each entry
        seen_entry_ids: set[int] = set()

        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Entry at index {i} in {location} must be a TournamentEntry - got {type(entry).__name__}')
            
            if self.tournament_id != entry.tournament_id:
                raise ValueError(
                    f'Entry {entry.id} at index {i} in {location} has tournament ID {entry.tournament_id}, '
                    f'which does not match the poule stage\'s tournament ID {self.tournament_id}'
                )
            
            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry {entry.id} exists more than once in entries in {location}')
            
            seen_entry_ids.add(entry.id)

    def _validate_seeded_entries(self, seeded_entries: tuple[SeededEntry, ...], method_name: str | None = None) -> None:
        """
        Validate the entries and initial seeds supplied for this stage.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            The seeded tournament entries to validate.
        method_name : str | None, optional
            The name of the method requesting validation.
            If None, only the class name is used in error messages.

        Raises
        ------
        TypeError
            If ``method_name`` is neither a string nor None,
            if ``seeded_entries`` is not a tuple, if an item is not a ``SeededEntry``,
            if an underlying entry is not a ``TournamentEntry``, or if a seed is not an integer.
        ValueError
            If fewer than two entries are supplied, if an entry belongs to another tournament,
            if an entry ID occurs more than once, if a seed is not positive or is repeated,
            or if the seeds are not exactly the integers from 1 through the number of entries.
        """
        location = 'PouleStage'

        if not isinstance(seeded_entries, tuple):
            raise TypeError(f'Seeded entries must be a tuple in {location} - got {type(seeded_entries).__name__}')

        if len(seeded_entries) < 2:
            raise ValueError(f'Seeded entries must contain at least 2 entries in {location} - got {len(seeded_entries)}')
        
        # Validate that each item is a seeded entry
        for i, seeded_entry in enumerate(seeded_entries):
            if not isinstance(seeded_entry, SeededEntry):
                raise TypeError(f'Seeded entry at index {i} in {location} must be a SeededEntry - got {type(seeded_entry).__name__}')

        # Validate all entries held by seeded entries
        entries = tuple(seeded_entry.entry for seeded_entry in seeded_entries)
        self._validate_entries(entries, method_name)

        # Validate the entry seeds held by the seeded entries
        seen_seeds: set[int] = set()
        
        for i, seeded_entry in enumerate(seeded_entries):
            seed = seeded_entry.seed

            validation.validate_positive_int(seed, f'Seed for seeded entry {seeded_entry.entry.id} at index {i}', 'PouleStage', method_name)

            if seed in seen_seeds:
                raise ValueError(f'Seed {seed} in seeded entries is assigned more than once in {location}')
            
            seen_seeds.add(seed)

        # Verify that all expected seeds are present
        expected_initial_seeds = set(range(1, len(seeded_entries) + 1))

        if seen_seeds != expected_initial_seeds:
            raise ValueError(
                f'Seeds in seeded entries in {location} must be a one-to-one mapping with '
                f'the integers from 1 through {len(seeded_entries)}'
            )

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
