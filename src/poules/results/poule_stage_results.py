from dataclasses import dataclass, field, InitVar
from itertools import groupby
from random import Random
from typing import NamedTuple

import validation

from entities.tournament_entry import TournamentEntry
from poules.poule_round import PouleRound
from poules.results.poule_stats import PouleStats
from poules.results.poule_stage_entry_result import PouleStageEntryResult
from tournament.results.stage.stage_results import StageResults
from tournament.results.stage.stage_entry_status import StageEntryStatus


class _PouleStanding(NamedTuple):
    """
    Store intermediate standing information for one entry.

    Used internally between ranking the aggregate statistics and 
    constructing the final PouleStageEntryResult objects.

    Attributes
    ----------
    entry : TournamentEntry
        The entry whose standing is represented.
    poule_stats : PouleStats
        The entry's aggregate statistics across the supplied rounds.
    position : int
        The entry's unique one-based position in ranking order.
    place : int
        The shared competition placement, 
        allowing ties and skipping subsequent places accordingly.
    is_tie : bool
        Whether another entry shares the same ranking criteria and placement.
    percentile : float
        The proportion of entries ranked below or equal to this entry, including the entry itself. 
        All members of a tied group share this value.
    """
    entry: TournamentEntry
    poule_stats: PouleStats
    position: int
    place: int
    is_tie: bool
    percentile: float


def _compute_percentile_rank(num_entries: int, num_below: int, num_equal: int) -> float:
    """
    Return the proportion of entries ranked below or equal to a group.

    Use the "weak" percentile-rank convention, 
    corresponding to the empirical cumulative distribution function: 
    count all entries strictly below the group and all entries in the group, 
    then divide by the total entry count.

    The result is expressed as a fraction rather than a percentage. 
    All members of the group receive the same percentile rank.

    Parameters
    ----------
    num_entries : int
        The positive total number of ranked entries.
    num_below : int
        The number of entries ranked strictly below the group.
    num_equal : int
        The number of entries in the group, 
        including the entry whose percentile rank is being calculated. 
        Must be at least one.

    Returns
    -------
    float
        The percentile rank, calculated as ``(num_below + num_equal) / num_entries``.
    """
    return (num_below + num_equal) / num_entries


@dataclass(frozen=True, slots=True)
class PouleStageResults(StageResults):
    """
    Represent a fixed snapshot of a poule stage's aggregate standings.

    Combine statistics by entry ID across the supplied rounds, using completed matches only. 
    Rank entries by victory ratio, indicator, and touches scored, in that priority order and all descending.

    Entries equal on all three ranking criteria share a place. 
    Their unique positions are ordered randomly within the tie. 
    This ordering does not affect shared placements or elimination decisions.

    The supplied rounds must belong to the same tournament and specified stage, 
    contain the same entry IDs, and be ordered consecutively from round 1. 
    All supplied rounds except the last must be complete.

    The supplied rounds are not stored. 
    Entry results retain references to their tournament entries. 
    This object's fields cannot be reassigned after initialization.

    Parameters
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    poule_rounds : list[PouleRound]
        A nonempty list of rounds ordered consecutively from round 1.
        The final supplied round may be incomplete.
    cut_value : float | None, default=None
        The percentile-rank cutoff in [0.0, 1.0). 
        Entries at or below the cutoff are marked ELIMINATED; 
        all others are marked ACTIVE.
        None is normalized to 0.0, which eliminates no entries.
    random_seed : int | None, default=None
        A non-negative seed used to order entries within complete ranking ties.
        If None, tie ordering is nondeterministic when creating a snapshot.

    Attributes
    ----------
    stage_number : int
        The stage number inherited from StageResults.
    cut_value : float
        The normalized cutoff applied to this snapshot.
    random_seed : int | None
        The seed supplied for ordering complete ranking ties.
    ranked_results : tuple[PouleStageEntryResult, ...]
        The calculated entry results in ranking order.

    Notes
    -----
    The caller decides whether a cut should apply, including whether the stage is complete. 
    This class does not infer stage completion from the supplied rounds. 
    Pass None or 0.0 when no cut should be applied.

    Cuts preserve ties and eliminate at most the configured proportion of entries. 
    Fewer entries may be eliminated because of ties or the discrete entry count. 
    A tied group crossing the cutoff advances together.
    """
    poule_rounds: InitVar[list[PouleRound]]
    cut_value: float | None = None
    random_seed: int | None = None
    _ranked_results: tuple[PouleStageEntryResult, ...] = field(init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, poule_rounds: list[PouleRound]) -> None:
        """
        Validate the inputs, normalize the cutoff, and calculate the snapshot.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The rounds from which to calculate aggregate statistics and standings.

        Raises
        ------
        TypeError
            If stage_number is not an integer, if poule_rounds is not a list
            or contains an item that is not a PouleRound, if cut_value is neither a float nor None, 
            or if random_seed is neither an integer nor None.
        ValueError
            If stage_number is not positive, if cut_value is outside [0.0, 1.0),
            if random_seed is negative, if poule_rounds is empty, 
            if the rounds do not share a tournament and the specified stage, 
            if their entry ID sets differ, if round numbers are not consecutive from 1,
            if any round except the last is incomplete, 
            or if a repeated entry ID refers to different fencer IDs across rounds.
        """
        location = self.__class__.__name__

        # Validate input parameters
        super(PouleStageResults, self).__post_init__()
        self._validate_poule_rounds(poule_rounds, location)
        
        if self.cut_value is not None:
            if not isinstance(self.cut_value, float):
                raise TypeError(f'Cut value must be a float or None in {location} - got {type(self.cut_value).__name__}')
            
            if not (0.0 <= self.cut_value < 1.0):
                raise ValueError(f'Cut value must be in the range [0.0, 1.0) in {location} - got {self.cut_value}')
        else:
            object.__setattr__(self, 'cut_value', 0.0)

        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', location)

        # Calculate the stage results based on the poule rounds
        object.__setattr__(self, '_ranked_results', self._calculate_ranked_results(poule_rounds))


    # --- Properties ---
    @property
    def ranked_results(self) -> tuple[PouleStageEntryResult, ...]:
        """Return the stored aggregate entry results in stage ranking order."""
        return self._ranked_results


    # --- Helper Methods ---
    def _calculate_ranked_results(self, poule_rounds: list[PouleRound]) -> tuple[PouleStageEntryResult, ...]:
        """
        Calculate the aggregate stage results from previously validated rounds.

        Accumulate entry statistics, rank the entries, determine placements and percentile ranks, 
        and apply the configured cutoff when constructing the final entry results.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The previously validated rounds whose results are combined.

        Returns
        -------
        tuple[PouleStageEntryResult, ...]
            One result per represented entry, in ranking order.

        Raises
        ------
        ValueError
            If entries sharing an ID across rounds refer to different fencer IDs.
        """
        entry_stats = self._accumulate_entry_stats(poule_rounds)
        ranked_items = self._rank_entry_stats(entry_stats)
        standings = self._calculate_standings(ranked_items)
        return self._build_entry_results(standings)

    def _accumulate_entry_stats(self, poule_rounds: list[PouleRound]) -> tuple[tuple[TournamentEntry, PouleStats], ...]:
        """
        Combine each entry's statistics across the supplied rounds.

        Add match, victory, and touch totals by entry ID.
        Derived statistics are calculated from these combined totals rather than averaged across rounds.

        Parameters
        ----------
        poule_rounds : list[PouleRound]
            The rounds whose calculated entry statistics are combined.

        Returns
        -------
        tuple[tuple[TournamentEntry, PouleStats], ...]
            One entry-statistics pair per unique entry ID, in first-encountered order. 
            Each pair contains the first encountered entry object and its accumulated statistics. 
            The pairs are not yet ranked.

        Raises
        ------
        ValueError
            If the same entry ID refers to different fencer IDs across rounds.
        """
        # Accumulate the results for each entry across all poule rounds
        results_tracker: dict[int, tuple[TournamentEntry, PouleStats]] = {}

        # Iterate through each poule round and accumulate the results for each entry
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
                            f'Entry ID {entry_id} refers to different fencers across poule rounds in {self.__class__.__name__}'
                            f' - expected fencer ID {stored_entry.fencer.id}, got {entry.fencer.id}'
                        )

                    results_tracker[entry_id] = (stored_entry, accumulated_stats + entry_result.poule_stats)

        return tuple(results_tracker.values())

    def _rank_entry_stats(self, entry_stats: tuple[tuple[TournamentEntry, PouleStats], ...]) -> tuple[tuple[TournamentEntry, PouleStats], ...]:
        """
        Order entry-statistics pairs by descending ranking criteria.

        Normalize the initial order by entry ID, 
        shuffle using random_seed, then apply a stable sort by victory ratio, indicator, and touches scored.
        The shuffled order is retained only within complete ranking ties.

        Parameters
        ----------
        entry_stats : tuple[tuple[TournamentEntry, PouleStats], ...]
            The entry objects and their aggregate statistics, with one pair per unique entry ID. 
            Pairs may be supplied in any order.

        Returns
        -------
        tuple[tuple[TournamentEntry, PouleStats], ...]
            The entry-statistics pairs in ranking order.

        Notes
        -----
        For identical entry IDs and statistics, 
        a fixed non-None random_seed produces reproducible tie ordering independently of the supplied order.
        Sorting and shuffling operate on a new list; the supplied tuple is not modified.
        """
        # Normalize entry order so seeded shuffling is reproducible
        ranked_items = sorted(entry_stats, key=lambda item: item[0].id)

        rng = Random(self.random_seed)
        rng.shuffle(ranked_items)

        # Stable sorting preserves shuffled order within complete ties
        ranked_items.sort(key=self._ranking_key, reverse=True)

        return tuple(ranked_items)

    @staticmethod
    def _ranking_key(item: tuple[TournamentEntry, PouleStats]) -> tuple[float, int, int]:
        """
        Return the criteria used to rank entries and identify complete ties.

        Parameters
        ----------
        item : tuple[TournamentEntry, PouleStats]
            An entry and its aggregate statistics.

        Returns
        -------
        tuple[float, int, int]
            Victory ratio, indicator, and touches scored, in ranking priority order. 
            Higher values rank ahead of lower values.
        """
        stats: PouleStats = item[1]
        return (stats.victory_ratio, stats.indicator, stats.touches_scored)

    def _calculate_standings(self, ranked_items: tuple[tuple[TournamentEntry, PouleStats], ...]) -> tuple[_PouleStanding, ...]:
        """
        Assign positions, shared places, tie flags, and percentile ranks.

        Process consecutive groups with equal ranking keys. 
        Positions are unique and consecutive from 1. 
        Each group shares the place of its first member.

        Each group's percentile rank is the proportion of all entries ranked below or equal to that group.

        Parameters
        ----------
        ranked_items : tuple[tuple[TournamentEntry, PouleStats], ...]
            Entry-statistics pairs already sorted in descending order by _ranking_key, with equal keys adjacent.

        Returns
        -------
        tuple[_PouleStanding, ...]
            One intermediate standing per entry, preserving the supplied order.
        """
        standings: list[_PouleStanding] = []
        num_entries = len(ranked_items)
        position = 1

        for _, group in groupby(ranked_items, key=self._ranking_key):
            tied_items = tuple(group)  # Consume and store group items to determine tie size
            num_equal = len(tied_items)

            place = position
            is_tie = num_equal > 1
            num_below = num_entries - (position - 1) - num_equal
            percentile = _compute_percentile_rank(num_entries, num_below, num_equal)

            for entry, stats in tied_items:
                standings.append(
                    _PouleStanding(
                        entry=entry,
                        poule_stats=stats,
                        position=position,
                        place=place,
                        is_tie=is_tie,
                        percentile=percentile
                    )
                )
                position += 1

        return tuple(standings)

    def _build_entry_results(self, standings: tuple[_PouleStanding, ...]) -> tuple[PouleStageEntryResult, ...]:
        """
        Construct entry result snapshots and apply the configured cutoff.

        Mark entries ELIMINATED when their percentile rank is at or below cut_value; otherwise, mark them ACTIVE. 
        Tied entries share a percentile rank and therefore receive the same status.

        Parameters
        ----------
        standings : tuple[_PouleStanding, ...]
            The calculated intermediate standings in ranking order.

        Returns
        -------
        tuple[PouleStageEntryResult, ...]
            The final entry snapshots in the same order as the supplied standings.
        """
        stage_results: list[PouleStageEntryResult] = []

        for standing in standings:
            status = StageEntryStatus.ELIMINATED if standing.percentile <= self.cut_value else StageEntryStatus.ACTIVE

            stage_results.append(
                PouleStageEntryResult(
                    entry=standing.entry,
                    stage_number=self.stage_number,
                    status=status,
                    position=standing.position,
                    place=standing.place,
                    is_tie=standing.is_tie,
                    poule_stats=standing.poule_stats
                )
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
            if any poule round has a different set of entries than the first round, 
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
                entry_ids: set[int] = set(entry.id for entry in poule_round.entries)

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

            if set(entry.id for entry in poule_round.entries) != entry_ids:
                raise ValueError(
                    f'Round at index {i} has different entries than the first round in {location}'
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
