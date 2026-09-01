from random import Random

from dataclasses import dataclass, field, InitVar

import validation

from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_result import PouleResult


@dataclass(frozen=True, slots=True)
class PouleStageResults:
    """
    Represents a fixed snapshot of a tournament's poule-stage results.

    The snapshot contains the result of each poule and the overall ranked
    results. Its fields cannot be reassigned after initialization.

    Parameters
    ----------
    poules : tuple[Poule, ...]
        The poules from which to calculate the result snapshots. 
        The poules themselves are not stored.
    random_seed : int | None, optional
        The seed used to resolve complete ranking ties. If `None`, ties are
        resolved nondeterministically.

    Attributes
    ----------
    random_seed : int | None
        The seed supplied for resolving complete ranking ties.
    poule_results : tuple[PouleResult, ...]
        The calculated result snapshot for each poule.
    stage_results : tuple[PouleEntryResult, ...]
        The entry results in descending ranking order.
    """
    poules: InitVar[tuple[Poule, ...]]
    random_seed: int | None = None

    poule_results: tuple[PouleResult, ...] = field(init=False)
    stage_results: tuple[PouleEntryResult, ...] = field(init=False)

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
            If `random_seed` is neither an integer nor `None`, 
            if `poules` is not a tuple, or if an item in `poules` is not a `Poule`.
        ValueError
            If `random_seed` is negative, if no poules are provided, 
            or if a poule number occurs more than once.
        """
        validation.validate_optional_non_negative_int(self.random_seed, 'random_seed', 'TournamentPouleResults')

        self._validate_poules(poules)

        object.__setattr__(self, 'poule_results', tuple(poule.calculate_results() for poule in poules))

        object.__setattr__(self, 'stage_results', self._calculate_stage_results())


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by these poule results."""
        return self.poule_results[0].tournament_id
    
    @property
    def stage_number(self) -> int:
        """Return the stage number shared by these poule results."""
        return self.poule_results[0].stage_number

    @property
    def stage_results_display_names(self) -> tuple[str, ...]:
        """Return the ranked entry results as fencer display names."""
        return tuple(entry_result.display_name for entry_result in self.stage_results)

    @property
    def label(self) -> str:
        """Return a descriptive label identifying these results."""
        return f'PouleStageResults for stage {self.stage_number} in tournament {self.tournament_id}'


    # --- Result Calculation Helper Methods ---
    def _calculate_stage_results(self) -> tuple[PouleEntryResult, ...]:
        """
        Calculates and ranks the overall results for the poule stage.

        Entries are ranked by victory ratio, indicator, and touches scored.
        Entries tied on all three criteria are ordered randomly.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending ranking order.
        """   
        stage_results: list[PouleEntryResult] = [entry_result for poule_result in self.poule_results for entry_result in poule_result.entry_results]

        rng = Random(self.random_seed)
        rng.shuffle(stage_results)

        stage_results.sort(key=lambda entry_result: (entry_result.victory_ratio, entry_result.indicator, entry_result.touches_scored), reverse=True)
    
        return tuple(stage_results)
    
    
    # --- Validation Helper Methods ---
    def _validate_poules(self, poules: tuple[Poule, ...]) -> None:
        """
        Validates that a given poules can belong in this poule stage.
        
        Parameters
        ----------
        poules : tuple[Poule, ...]
            The poules to validate.

        Raises
        ------
        TypeError
            If `poules` is not a tuple, or if any entry in `poules` is not a `Poule` object.
        ValueError
            If `poules` is an empty tuple, 
            if a poule's tournament ID or stage number differs from the other poules, 
            or if any poule occurs more than once in the tuple.
        """
        if not isinstance(poules, tuple):
            raise TypeError(f'The given set of poules must be in a tuple - got {type(poules).__name__}')
        
        if not poules:
            raise ValueError(f'The given set of poules cannot be empty - got {len(poules)}')

        seen_poule_numbers: set[int] = set()

        for i, poule in enumerate(poules):
            if not isinstance(poule, Poule):
                raise TypeError(f'Entry at index {i} must be a Poule object - got {type(poule).__name__}')

            if i == 0:
                tournament_id: int = poule.tournament_id
                stage_number: int = poule.stage_number

            if poule.tournament_id != tournament_id:
                raise ValueError(f'Poule {poule.poule_number} at index {i} has a tournament ID {poule.tournament_id} that does not match the other poules\' tournament IDs {tournament_id}')
            
            if poule.stage_number != stage_number:
                raise ValueError(f'Poule {poule.poule_number} at index {i} has a stage number {poule.stage_number} that does not match the other poules\' stage numbers {stage_number}')

            if poule.poule_number in seen_poule_numbers:
                raise ValueError(f'Poule number {poule.poule_number} occurs more than once.')
            
            seen_poule_numbers.add(poule.poule_number)
