from random import Random

from dataclasses import dataclass, field, InitVar

import validation

from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_result import PouleResult


@dataclass(frozen=True, slots=True)
class TournamentPouleResults:
    """
    Represents a fixed snapshot of a tournament's poule-round results.

    The snapshot contains the result of each poule and the overall ranked
    results. Its fields cannot be reassigned after initialization.

    Parameters
    ----------
    tournament_id : int
        The unique identifier of the tournament.
    poules : tuple[Poule, ...]
        The poules from which to calculate the result snapshots. 
        The poules themselves are not stored.
    random_seed : int | None, optional
        The seed used to resolve complete ranking ties. If `None`, ties are
        resolved nondeterministically.

    Attributes
    ----------
    tournament_id : int
        The unique identifier of the tournament these results belong to.
    random_seed : int | None
        The seed supplied for resolving complete ranking ties.
    poule_results : tuple[PouleResult, ...]
        The calculated result snapshot for each poule.
    round_results : tuple[PouleEntryResult, ...]
        The entry results in descending ranking order.
    """
    tournament_id: int
    poules: InitVar[tuple[Poule, ...]]
    random_seed: int | None = None

    poule_results: tuple[PouleResult, ...] = field(init=False)
    round_results: tuple[PouleEntryResult, ...] = field(init=False)

    # --- Initialization and Validation Methods ---
    def __post_init__(self, poules: tuple[Poule, ...]) -> None:
        """
        Parameters
        ----------
        poules : tuple[Poule, ...]
            The poules for which to hold the results for.

        Raises
        ------
        TypeError
            If the tournament ID is not an integer, if `random_seed` is neither an
            integer nor `None`, if `poules` is not a tuple, or if an item in
            `poules` is not a `Poule`.
        ValueError
            If the tournament ID is non-positive, if `random_seed` is negative, if
            no poules are provided, if a poule belongs to another tournament, or if
            a poule ID occurs more than once.
        """
        validation.validate_positive_int(self.tournament_id, 'tournament ID', 'TournamentPouleResults')
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', 'TournamentPouleResults')

        self._validate_poules(poules)

        object.__setattr__(self, 'poule_results', tuple(poule.calculate_results() for poule in poules))

        object.__setattr__(self, 'round_results', self._calculate_round_results())


    # --- Properties ---
    @property
    def round_results_display_names(self) -> tuple[str, ...]:
        """Return the ranked entry results as fencer display names."""
        return tuple(entry_result.display_name for entry_result in self.round_results)


    # --- Result Calculation Helper Methods ---
    def _calculate_round_results(self) -> tuple[PouleEntryResult, ...]:
        """
        Calculates and ranks the overall results for the poule round.

        Entries are ranked by victory ratio, indicator, and touches scored.
        Entries tied on all three criteria are ordered randomly.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending ranking order.
        """   
        round_results: list[PouleEntryResult] = [entry_result for poule_result in self.poule_results for entry_result in poule_result.entry_results]

        rng = Random(self.random_seed)
        rng.shuffle(round_results)

        round_results.sort(key=lambda entry_result: (entry_result.victory_ratio, entry_result.indicator, entry_result.touches_scored), reverse=True)
    
        return tuple(round_results)
    
    
    # --- Validation Helper Methods ---
    def _validate_poules(self, poules: tuple[Poule, ...]) -> None:
        """
        Validates that a given poules can belong in this poule round.
        
        Parameters
        ----------
        poules : tuple[Poule, ...]
            The poules to validate.

        Raises
        ------
        TypeError
            If `poules` is not a tuple, or if any entry in `poules` is not a `Poule` object.
        ValueError
            If `poules` is an empty tuple, if any poule's tournament ID does not match the poule round's tournament ID, 
            or if any poule occurs more than once in the tuple.
        """
        if not isinstance(poules, tuple):
            raise TypeError(f'The given set of poules must be in a tuple - got {type(poules).__name__}')
        
        if not poules:
            raise ValueError(f'The given set of poules cannot be empty - got {len(poules)}')

        seen_poule_ids: set[int] = set()

        for i, poule in enumerate(poules):
            if not isinstance(poule, Poule):
                raise TypeError(f'Entry at index {i} must be a Poule object - got {type(poule).__name__}')

            if poule.tournament_id != self.tournament_id:
                raise ValueError(f'Poule {poule.id} at index {i} has a tournament ID {poule.tournament_id} that does not match the poule round\'s tournament ID {self.tournament_id}')
            
            if poule.id in seen_poule_ids:
                raise ValueError(f'Poule ID {poule.id} occurs more than once.')
            
            seen_poule_ids.add(poule.id)