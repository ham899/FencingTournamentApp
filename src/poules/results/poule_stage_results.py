from dataclasses import dataclass, field, InitVar
from random import Random

import validation

from entities.tournament_entry import TournamentEntry
from poules.poule_round import PouleRound
from poules.results.poule_stats import PouleStats
from poules.results.poule_stage_entry_result import PouleStageEntryResult


@dataclass(frozen=True, slots=True)
class PouleStageResults:
    """
    Represents a fixed snapshot of a poule stage's aggregate results.

    Statistics are combined by entry ID across the supplied poule rounds.
    Only completed matches contribute to the statistics. 
    All supplied rounds except the last must be complete.

    The rounds must belong to the same tournament and the specified stage,
    and must be ordered consecutively from round 1.

    The supplied rounds are not stored. 
    The calculated entry results retain references to their tournament entries. 
    This object's fields cannot be reassigned after initialization.

    The ``ranked_results`` tuple contains the aggregate stage ranking.
    The ``ranked_entries`` and ``ranked_names`` properties follow that same order.

    Parameters
    ----------
    stage_number : int
        The poule stage's one-based position within the tournament.
    poule_rounds : list[PouleRound]
        A nonempty list of rounds ordered consecutively from round 1.
        All rounds except the last must be complete.
    random_seed : int | None, optional
        A nonnegative seed used to order complete ranking ties.
        If None, tie ordering is nondeterministic.

    Attributes
    ----------
    stage_number : int
        The poule stage's one-based position within the tournament.
    random_seed : int | None
        The seed supplied for ordering complete ranking ties.
    ranked_results : tuple[PouleStageEntryResult, ...]
        The aggregate entry results ranked by victory ratio, indicator, and touches scored, 
        all in descending order. Complete ties are ordered randomly.
    """
    stage_number: int
    poule_rounds: InitVar[list[PouleRound]]
    random_seed: int | None = None
    ranked_results: tuple[PouleStageEntryResult, ...] = field(init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, poule_rounds: list[PouleRound]) -> None:
        """
        Validate the supplied parameters and calculate the stage's result snapshot.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The rounds from which to calculate the aggregate entry results
            and overall stage ranking.

        Raises
        ------
        TypeError
            If ``stage_number`` is not an integer, if ``random_seed`` is neither
            an integer nor None, if ``poule_rounds`` is not a list, or if an
            item in ``poule_rounds`` is not a ``PouleRound``.
        ValueError
            If ``stage_number`` is not positive, if ``random_seed`` is negative,
            if ``poule_rounds`` is empty, if the rounds do not share a tournament ID 
            or belong to the specified stage, if round numbers are not consecutive from 1 in supplied order, 
            if any round except the last is incomplete, 
            or if entries sharing an ID across rounds refer to different fencer IDs.
        """
        location = 'PouleStageResults'

        # Validate input parameters
        validation.validate_positive_int(self.stage_number, 'stage_number', location)
        self._validate_poule_rounds(poule_rounds, location)
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', location)

        # Calculate the stage results based on the poule rounds
        object.__setattr__(self, 'ranked_results', self._calculate_ranked_results(poule_rounds))


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the represented entries."""
        return self.ranked_results[0].entry.tournament_id

    @property
    def num_entries(self) -> int:
        """Return the number of represented entries."""
        return len(self.ranked_results)

    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the tournament entries in the same order as ranked_results."""
        return tuple(result.entry for result in self.ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the entry display names in the same order as ranked_results."""
        return tuple(result.display_name for result in self.ranked_results)


    # --- Helper Methods ---
    def _calculate_ranked_results(self, poule_rounds: list[PouleRound]) -> tuple[PouleStageEntryResult, ...]:
        """
        Combine and rank each entry's statistics across the supplied rounds.

        Statistics are accumulated by entry ID using the flattened results from each round. 
        Victory ratios are calculated from the combined victory and match totals, 
        rather than averaging individual round ratios.

        Entries are ranked by victory ratio, indicator, and touches scored,
        in that priority order and all descending.

        For the same entry IDs and aggregate statistics, 
        a fixed non-None ``random_seed`` produces reproducible tie ordering independent of input entry order.
        With ``random_seed=None``, complete ties are ordered nondeterministically.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The previously validated rounds from which to calculate the aggregate entry results.

        Returns
        -------
        tuple[PouleStageEntryResult, ...]
            One aggregate result per entry encountered across the supplied rounds, in ranking order.

        Raises
        ------
        ValueError
            If entries sharing an ID across rounds refer to different fencer IDs.
        """
        # Accumulate the results for each entry across all poule rounds
        results_tracker: dict[int, tuple[TournamentEntry, PouleStats]] = {}

        for poule_round in poule_rounds:
            round_results = poule_round.calculate_results().poule_results_flattened

            for entry_result in round_results:
                entry = entry_result.entry
                entry_id = entry.id

                if entry_id not in results_tracker:
                    results_tracker[entry_id] = (entry, entry_result.poule_stats)
                else:
                    stored_entry, accumulated_stats = results_tracker[entry_id]

                    if stored_entry.fencer.id != entry.fencer.id:
                        raise ValueError(
                            f'Entry ID {entry_id} refers to different fencers across poule rounds in PouleStageResults'
                            f' - expected fencer ID {stored_entry.fencer.id}, got {entry.fencer.id}'
                        )

                    results_tracker[entry_id] = (stored_entry, accumulated_stats + entry_result.poule_stats)

        # Add the results from the results tracker to the stage results
        stage_results: list[PouleStageEntryResult] = []

        for results in results_tracker.values():
            stage_results.append(
                PouleStageEntryResult(
                    entry=results[0],
                    stage_number=self.stage_number,
                    poule_stats=results[1]
                )
            )

        # Shuffle the results to ensure that complete ties are ordered randomly
        stage_results.sort(key=lambda result: result.entry.id)  # Sort by entry ID to ensure deterministic shuffling

        rng = Random(self.random_seed)
        rng.shuffle(stage_results)

        # Sort the results by victory ratio, indicator, and touches scored, all in descending order
        stage_results.sort(
            key=lambda result: (result.victory_ratio, result.indicator, result.touches_scored), reverse=True
        )

        return tuple(stage_results)


    # --- Validation Helper Methods ---
    def _validate_poule_rounds(self, poule_rounds: list[PouleRound], location: str) -> None:
        """
        Validate that the supplied rounds form a sequence within one poule stage.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The poule rounds to validate.
        location : str
            The class name to use in validation error messages.

        Raises
        ------
        TypeError
            If ``poule_rounds`` is not a list or an item is not a PouleRound.
        ValueError
            If ``poule_rounds`` is empty, 
            if the rounds do not share a tournament ID or belong to the specified stage, 
            if round numbers are not consecutive from 1 in supplied order, 
            or if any round except the last is incomplete.
        """
        if not isinstance(poule_rounds, list):
            raise TypeError(
                f'Poule rounds must be a list in {location} - got {type(poule_rounds).__name__}'
            )

        if not poule_rounds:
            raise ValueError(f'At least one poule round must be supplied in {location}')

        for i, poule_round in enumerate(poule_rounds):
            if not isinstance(poule_round, PouleRound):
                raise TypeError(
                    f'Item at index {i} in poule_rounds must be a PouleRound in {location} - '
                    f'got {type(poule_round).__name__}'
                )

            if i == 0:
                tournament_id = poule_round.tournament_id

            if poule_round.tournament_id != tournament_id:
                raise ValueError(
                    f'Round at index {i} belongs to another tournament in {location} - '
                    f'expected {tournament_id}, got {poule_round.tournament_id}'
                )

            if poule_round.stage_number != self.stage_number:
                raise ValueError(
                    f'Round at index {i} belongs to another stage in {location} - '
                    f'expected {self.stage_number}, got {poule_round.stage_number}'
                )

            expected_round_number = i + 1

            if poule_round.round_number != expected_round_number:
                raise ValueError(
                    f'Poule rounds must be ordered consecutively from 1 in {location} - '
                    f'expected round number {expected_round_number}, got {poule_round.round_number}'
                )

        for poule_round in poule_rounds[:-1]:
            if poule_round.is_incomplete():
                raise ValueError(
                    f'All poule rounds except the last must be complete in {location} - '
                    f'round {poule_round.round_number} is incomplete'
                )
