from random import Random

from dataclasses import dataclass, field, InitVar

import validation

from entities import TournamentEntry
from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_result import PouleResult


@dataclass(frozen=True, slots=True)
class PouleRoundResults:
    """
    Represents a fixed snapshot of a poule round's current results.

    The snapshot contains each poule's results and the combined ranking of entries across all supplied poules. 
    Only completed matches contribute to the statistics; the round does not need to be complete.

    All poules must belong to the same tournament, stage, and round.
    Poule numbers and entry IDs must be unique across the supplied poules.

    The poules themselves are not stored. 
    The calculated result snapshots retain references to their tournament entries. 
    This object's fields cannot be reassigned after initialization.

    The `ranked_results` tuple contains the combined round ranking.
    The `ranked_entries` and `ranked_names` properties follow that same order.
    The `poule_results_flattened` property instead preserves supplied poule order and the entry order within each poule.

    Parameters
    ----------
    poules : tuple[Poule, ...]
        A nonempty tuple of poules from which to calculate the results.
    random_seed : int | None, optional
        A nonnegative seed used to order complete ranking ties.
        If `None`, tie ordering is nondeterministic.

    Attributes
    ----------
    random_seed : int | None
        The seed supplied for ordering complete ranking ties.
    poule_results : tuple[PouleResult, ...]
        The calculated poule snapshots, in the order the poules were supplied.
    ranked_results : tuple[PouleEntryResult, ...]
        The entry results ranked by victory ratio, indicator, and touches scored, all in descending order. 
        Complete ties are ordered randomly.
    """
    poules: InitVar[tuple[Poule, ...]]
    random_seed: int | None = None

    poule_results: tuple[PouleResult, ...] = field(init=False)
    ranked_results: tuple[PouleEntryResult, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, poules: tuple[Poule, ...]) -> None:
        """
        Validate the supplied poules and calculate the round's result snapshot.

        Parameters
        ----------
        poules : tuple[Poule, ...]
            The poules from which to calculate individual poule snapshots and
            the overall round ranking.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`, if `poules` is not a tuple, 
            or if an item in `poules` is not a `Poule`.
        ValueError
            If `random_seed` is negative, if `poules` is empty, if the poules do not share a tournament ID, 
            stage number, and round number, if a poule number is repeated, 
            or if an entry ID occurs more than once across the supplied poules.
        """
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', 'PouleRoundResults')
        self._validate_poules(poules)
        object.__setattr__(self, 'poule_results', tuple(poule.calculate_results() for poule in poules))
        object.__setattr__(self, 'ranked_results', self._calculate_ranked_results())


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying these results."""
        return (
            f'PouleRoundResults for round {self.round_number} '
            f'of stage {self.stage_number} in tournament {self.tournament_id}'
        )

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by these poule results."""
        return self.poule_results[0].tournament_id

    @property
    def stage_number(self) -> int:
        """Return the stage number shared by these poule results."""
        return self.poule_results[0].stage_number

    @property
    def round_number(self) -> int:
        """Return the round number shared by these poule results."""
        return self.poule_results[0].round_number

    @property
    def num_entries(self) -> int:
        """Return the number of represented entries."""
        return len(self.ranked_results)

    @property
    def poule_results_flattened(self) -> tuple[PouleEntryResult, ...]:
        """
        Return the entry results from all poule snapshots without ranking them.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in supplied poule order, 
            preserving the entry order within each poule snapshot.
        """
        return tuple(
            entry_result
            for poule_result in self.poule_results
            for entry_result in poule_result.entry_results
        )
    
    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the entries in the same order as ranked_results."""
        return tuple(result.entry for result in self.ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the entry display names in the same order as ranked_results."""
        return tuple(entry_result.display_name for entry_result in self.ranked_results)


    # --- Result Calculation Helper Methods ---
    def _calculate_ranked_results(self) -> tuple[PouleEntryResult, ...]:
        """
        Combine and rank the entry results from all poule snapshots.

        Entries are ranked by victory ratio, indicator, and touches scored,
        in that priority order and all descending.

        For the same entry IDs and statistics, 
        a fixed non-None ``random_seed`` produces reproducible tie ordering independent of input entry order.
        With ``random_seed=None``, complete ties are ordered nondeterministically.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            One result per entry across the supplied poules, in ranking order.
        """
        entry_results: list[PouleEntryResult] = [
            entry_result for poule_result in self.poule_results for entry_result in poule_result.entry_results
        ]

        rng = Random(self.random_seed)

        # Normalize entry order before shuffling so seeded ties do not depend on input order
        entry_results.sort(key=lambda result: result.entry.id)
        rng.shuffle(entry_results)


        entry_results.sort(key=lambda entry_result: (entry_result.victory_ratio, entry_result.indicator, entry_result.touches_scored), reverse=True)

        return tuple(entry_results)


    # --- Validation Helper Methods ---
    def _validate_poules(self, poules: tuple[Poule, ...]) -> None:
        """
        Validate that the supplied poules can belong to one poule round.

        Require a nonempty tuple of poules sharing a tournament ID, stage number, and round number. 
        Poule numbers and entry IDs must be unique across the supplied poules.

        Parameters
        ----------
        poules : tuple[Poule, ...]
            The poules to validate.

        Raises
        ------
        TypeError
            If `poules` is not a tuple or an item is not a `Poule`.
        ValueError
            If `poules` is empty, if a poule's tournament ID, stage number, or round number differs from the others, 
            if a poule number is repeated, or if an entry ID occurs more than once across the supplied poules.
        """
        if not isinstance(poules, tuple):
            raise TypeError(f'The given set of poules must be in a tuple - got {type(poules).__name__}')
        
        if not poules:
            raise ValueError(f'The given set of poules cannot be empty - got {len(poules)}')

        seen_poule_numbers: set[int] = set()
        seen_entry_ids: set[int] = set()

        for i, poule in enumerate(poules):
            if not isinstance(poule, Poule):
                raise TypeError(f'Entry at index {i} must be a Poule object - got {type(poule).__name__}')

            if i == 0:
                tournament_id: int = poule.tournament_id
                stage_number: int = poule.stage_number
                round_number: int = poule.round_number

            if poule.tournament_id != tournament_id:
                raise ValueError(
                    f'Poule {poule.poule_number} at index {i} has a tournament ID {poule.tournament_id}'
                    f' that does not match the other poules\' tournament IDs {tournament_id}'
                )

            if poule.stage_number != stage_number:
                raise ValueError(
                    f'Poule {poule.poule_number} at index {i} has a stage number {poule.stage_number} '
                    f'that does not match the other poules\' stage numbers {stage_number}'
                )

            if poule.round_number != round_number:
                raise ValueError(
                    f'Poule {poule.poule_number} at index {i} has a round number {poule.round_number} '
                    f'that does not match the other poules\' round numbers {round_number}'
                )

            if poule.poule_number in seen_poule_numbers:
                raise ValueError(f'Poule number {poule.poule_number} occurs more than once.')

            seen_poule_numbers.add(poule.poule_number)

            for entry in poule.entries:
                if entry.id in seen_entry_ids:
                    raise ValueError(
                        f'Entry ID {entry.id} occurs more than once across the supplied poules'
                    )
                seen_entry_ids.add(entry.id)
