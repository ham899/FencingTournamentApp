from dataclasses import dataclass, field

import validation

from entities.seeded_entry import SeededEntry
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_stage_results import PouleStageResults
from utils import snake_numbers


@dataclass(eq=False)
class PouleStage:
    """
    Represent a stage in a tournament where poules are conducted.

    A poule stage distributes each entry into exactly one poule using snake seeding,
    and coordinates match access and result calculation across those poules.
    
    Attributes
    ----------
    seeded_entries : tuple[SeededEntry, ...]
        The entries and their seeds for this stage. Each underlying entry must
        belong to the same tournament and occur exactly once. Seeds must be a
        one-to-one mapping with the integers from 1 through the number of entries.
        Seeded entries are stored in ascending seed order.
    stage_number : int
        The poule stage's one-based position within the tournament.
    score_to_win : int, default=5
        The target score and maximum permitted recorded score for either entry.
    poules : tuple[Poule, ...]
        The generated poules in poule-number order.
    """
    stage_number: int
    seeded_entries: tuple[SeededEntry, ...]
    score_to_win: int = field(default=5, kw_only=True)
    poules: tuple[Poule, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the stage, sorts its seeded entries by seed, and generates its poules.

        Raises
        ------
        TypeError
            If `stage_number` or `score_to_win` is not an integer, if `entries` is not a tuple, 
            if an item is not a `SeededEntry`, or if a seed is not an integer.
        ValueError
            If `stage_number` or `score_to_win` is not positive, 
            if fewer than two entries are provided, 
            if an entry belongs to another tournament or appears more than once, 
            if a seed is missing, non-positive, or repeated, 
            or if the seeds are not exactly the integers from 1 through the number of entries.
        """
        validation.validate_positive_int(self.stage_number, 'Stage number', 'PouleStage')
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'PouleStage')
        
        self._validate_seeded_entries(self.seeded_entries)

        self.seeded_entries = tuple(sorted(self.seeded_entries, key=lambda seeded_entry: seeded_entry.seed))
        
        self.poules = self._generate_poules(self.entries)


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the poule stage."""
        return f'PouleStage in stage {self.stage_number} in tournament {self.tournament_id}'

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the entries in this stage."""
        return self.seeded_entries[0].entry.tournament_id

    @property
    def num_poules(self) -> int:
        """Return the number of poules in this stage."""
        return len(self.poules)

    @property
    def num_entries(self) -> int:
        """Return the number of entries in this stage."""
        return len(self.seeded_entries)

    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """Return the tournament entries in ascending stage-seed order."""
        return tuple(seeded_entry.entry for seeded_entry in self.seeded_entries)
    
    
    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """Return whether another object represents the same poule stage."""
        if not isinstance(other, PouleStage):
            return False
        
        return self.stage_number == other.stage_number and self.tournament_id == other.tournament_id


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Return whether any poule in this stage has started."""
        return any(poule.has_started() for poule in self.poules)

    def is_complete(self) -> bool:
        """Return whether every poule in this stage is complete."""
        return all(poule.is_complete() for poule in self.poules)
    

    # --- Poule Access Methods ---
    def get_poule_at(self, index: int) -> Poule:
        """
        Return the poule at a specified index.
        
        Parameters
        ----------
        index : int
            The poule's zero-based position in the stage.

        Returns
        -------
        Poule
            The poule at the index.

        Raises
        ------
        TypeError
            If `index` is not an integer.
        ValueError
            If `index` is outside the valid range of poule indices.
        """
        self._validate_poule_index(index, 'get_poule_at')
        return self.poules[index]
    
    def get_match_at(self, poule_index: int, match_index: int) -> PouleMatch:
        """
        Return a match from a specified poule.
        
        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the stage.
        match_index : int
            The match's zero-based position in the poule's official bout order.

        Returns
        -------
        PouleMatch
            The match at the specified poule and match indices.

        Raises
        ------
        TypeError
            If `poule_index` or `match_index` is not an integer.
        ValueError
            If either index is outside its respective valid range.
        """
        self._validate_poule_index(poule_index, 'get_match_at')
        return self.poules[poule_index].get_match_at(match_index)

    def get_on_piste_match(self, poule_index: int) -> PouleMatch | None:
        """
        Return the match that should currently be on piste in the specified poule.

        The first incomplete match in the official bout order is returned.

        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the stage.

        Returns
        -------
        PouleMatch | None
            The match that should be on piste, or None if the poule is complete.

        Raises
        ------
        TypeError
            If `poule_index` is not an integer.
        ValueError
            If `poule_index` is outside the valid range of poule indices.

        Notes
        -----
        This method assumes that each poule is being run one match at a time on one piste.
        """
        self._validate_poule_index(poule_index, 'get_on_piste_match')
        return self.poules[poule_index].get_on_piste_match()

    def get_on_deck_match(self, poule_index: int) -> PouleMatch | None:
        """
        Return the next match waiting to fence in the specified poule.

        The on-piste match is excluded, 
        and the first remaining incomplete match in the official bout order is returned.
        
        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the stage.

        Returns
        -------
        PouleMatch | None
            The match on deck, or None if no match is waiting to fence.

        Raises
        ------
        TypeError
            If `poule_index` is not an integer.
        ValueError
            If `poule_index` is outside the valid range of poule indices.
        """
        self._validate_poule_index(poule_index, 'get_on_deck_match')
        return self.poules[poule_index].get_on_deck_match()
    

    # --- Match Result Recording Methods ---
    def record_match_result(self, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Record the result of a specified match in a specified poule.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule containing the match.
        match_index : int
            The match's zero-based position in the official bout order.
        score1 : int
            The score to record for the first entry in the match.
        score2 : int
            The score to record for the second entry in the match.

        Raises
        ------
        TypeError
            If either index or either score is not an integer.
        ValueError
            If either index is outside its valid range, the match is already complete, 
            or the scores do not form a valid completed result.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_match_result(match_index, score1, score2)

    def record_on_piste_match_result(self, poule_index: int, score1: int, score2: int) -> None:
        """
        Record the result of the on-piste match in a specified poule.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule.
        score1 : int
            The score to record for the first entry in the match.
        score2 : int
            The score to record for the second entry in the match.

        Raises
        ------
        TypeError
            If `poule_index` or either score is not an integer.
        ValueError
            If ``poule_index`` is outside its valid range,
            either score is outside the permitted range, or the scores are equal.
        RuntimeError
            If the poule is complete and therefore has no on-piste match.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_on_piste_match_result(score1, score2)

    def record_forfeit(self, poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for the match at the specified index.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule.
        match_index : int
            The zero-based position of the match for which to record the forfeit.
        forfeiting_index : int
            The index of the forfeiting entry - ``0`` for entry 1 and ``1`` for entry 2.

        Raises
        ------
        TypeError
            If any index is not an integer.
        ValueError
            If ``poule_index`` or ``match_index`` is outside its valid range,
            ``forfeiting_index`` is not ``0`` or ``1``, or the match is already complete.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_forfeit(match_index, forfeiting_index)

    def replace_with_score(self, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Replace the specified match's scored or forfeit result with new scores.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule.
        match_index : int
            The zero-based index of the match for which to replace the result.
        score1 : int
            The new score for entry 1.
        score2 : int
            The new score for entry 2.

        Raises
        ------
        TypeError
            If either index or either score is not an integer.
        ValueError
            If either index is outside its valid range, either score is outside the permitted range, 
            the scores are equal, or the match is incomplete.
        """
        poule = self.get_poule_at(poule_index)
        poule.replace_with_score(match_index, score1, score2)

    def replace_with_forfeit(self, poule_index: int, match_index: int, forfeiting_index: int) -> None:
        """
        Replace the specified match's scored or forfeit result with a forfeit.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule.
        match_index : int
            The zero-based index of the match for which to replace the result.
        forfeiting_index : int
            The index of the forfeiting entry: ``0`` for entry 1 and ``1`` for entry 2.

        Raises
        ------
        TypeError
            If any index is not an integer.
        ValueError
            If ``poule_index`` or ``match_index`` is outside its valid range,
            ``forfeiting_index`` is not ``0`` or ``1``, or the match is incomplete.
        """
        poule = self.get_poule_at(poule_index)
        poule.replace_with_forfeit(match_index, forfeiting_index)


    # --- Result Calculation Methods ---
    def calculate_results(self, random_seed: int | None = None) -> PouleStageResults:
        """
        Calculate and return a snapshot of the poule stage's current results.

        The matches in each poule remain the source of truth. 
        Complete ranking ties are shuffled using `random_seed`.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order ranking ties. 

        Returns
        -------
        TournamentPouleResults
            A newly calculated snapshot of the results across all poules.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return PouleStageResults(self.poules, random_seed)
    
    def calculate_ranked_results(self, random_seed: int | None = None) -> tuple[PouleEntryResult, ...]:
        """
        Calculate and return the stage's entry results in ranked order.

        Entries are ranked by victory ratio, indicator, and touches scored, all in descending order. 
        Ties are shuffled using `random_seed`.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order ranking ties. 

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending rank order.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return self.calculate_results(random_seed).stage_results
    
    def calculate_ranked_results_display_names(self, random_seed: int | None = None) -> tuple[str, ...]:
        """
        Calculate and return entry display names in stage ranking order.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order ranking ties. 

        Returns
        -------
        tuple[str, ...]
            The entries' display names in descending rank order.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return self.calculate_results(random_seed).stage_results_display_names


    # --- Creation Helper Methods ---
    def _calculate_poule_sizes(self, num_entries: int, max_poule_size: int = 7) -> tuple[int, ...]:
        """
        Calculate balanced poule sizes for a specified number of entries.

        The number of poules is minimized, no poule exceeds `max_poule_size`,
        and the poules differ in size by at most one.

        Parameters
        ----------
        num_entries : int
            The number of entries to distribute.
        max_poule_size : int, optional, default=7
            The maximum allowable poule size.

        Returns
        -------
        tuple[int, ...]
            The size of each poule, with larger poules appearing first.

        Raises
        ------
        TypeError
            If `num_entries` or `max_poule_size` is not an integer.
        ValueError
            If `num_entries` is less than 2 or `max_poule_size` is less than 3.
        """
        validation.validate_int_at_least(num_entries, 2, 'num_entries', 'PouleStage', '_calculate_poule_sizes')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleStage', '_calculate_poule_sizes')

        # The minimal number of poules required is the smallest integer that satisfies 
        # the inequality: num_poules * max_poule_size >= num_entries
        num_poules = (num_entries + max_poule_size - 1) // max_poule_size # equivalent to ceil(num_entries / max_poule_size)

        integer_quotient, remainder = divmod(num_entries, num_poules)

        # Only a difference of one in poule size in poules is allowed upon stage initialization
        larger_poule_size = integer_quotient + 1
        smaller_poule_size = integer_quotient

        num_larger_poules = remainder
        num_smaller_poules = num_poules - num_larger_poules

        return (larger_poule_size,) * num_larger_poules + (smaller_poule_size,) * num_smaller_poules

    def _assign_entries_to_poules(self, entries: tuple[TournamentEntry, ...], poule_sizes: tuple[int, ...]) -> tuple[tuple[TournamentEntry, ...], ...]:
        """
        Assigns entries to poules using snake distribution.

        Entries are assigned in their supplied order. 
        This method therefore expects `entries` to already be in the intended seeding order.
        
        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The validated entries in the order in which they should be distributed.
        poule_sizes : tuple[int, ...]
            The target size of each poule in poule-index order.

        Returns
        -------
        tuple[tuple[TournamentEntry, ...], ...]
            The entries assigned to each poule in poule-index order.

        Raises
        ------
        TypeError
            If `entries` is not a tuple; an item is not a `TournamentEntry`; 
            `poule_sizes` is not a tuple; or a poule size is not an integer.
        ValueError
            If `entries` violates the stage's membership or uniqueness requirements; 
            `poule_sizes` is empty; a poule size is less than 2; 
            or the poule sizes do not sum to the number of entries.
        """
        # Validate inputs
        self._validate_entries(entries, '_assign_entries_to_poules')
        
        if not isinstance(poule_sizes, tuple):
            raise TypeError(
                f'poule_sizes must be a tuple in PouleStage._assign_entries_to_poules() - got {type(poule_sizes).__name__}'
            )

        if not poule_sizes:
            raise ValueError(
                f'poule_sizes must contain at least 1 poule size in PouleStage._assign_entries_to_poules() - got {len(poule_sizes)}'
            )

        for size in poule_sizes:
            validation.validate_int_at_least(size, 2, 'a poule size in poule_sizes', 'PouleStage', '_assign_entries_to_poules')

        if sum(poule_sizes) != len(entries):
            raise ValueError(
                f'The sum of poule_sizes must equal the number of entries in PouleStage._assign_entries_to_poules() '
                f'- got sum={sum(poule_sizes)} and num_entries={len(entries)}'
            )

        # Initialize variables needed for distribution
        num_poules = len(poule_sizes)
        entries_by_poule = [[] for _ in range(num_poules)]
        snake_generator = snake_numbers(num_poules)
        
        # Distribute entries to their respective poules
        for entry in entries:
            poule_index = next(snake_generator)

            while len(entries_by_poule[poule_index]) >= poule_sizes[poule_index]:
                poule_index = next(snake_generator)

            entries_by_poule[poule_index].append(entry)

        # Convert and return the entries for each poule as a tuple of tuples
        return tuple(tuple(poule_entries) for poule_entries in entries_by_poule)

    def _generate_poules(self, entries: tuple[TournamentEntry, ...], max_poule_size: int = 7) -> tuple[Poule, ...]:
        """
        Generate the poules for a collection of entries.

        Entries are distributed in their supplied order, so they must already be ordered by ascending seed.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The validated entries in ascending seed order.
        max_poule_size : int, optional, default=7
            The maximum allowable poule size.

        Returns
        -------
        tuple[Poule, ...]
            The generated poules in poule-number order.

        Raises
        ------
        TypeError
            If `entries` is not a tuple; an item is not a `TournamentEntry`; 
            or `max_poule_size` is not an integer.
        ValueError
            If `entries` violates the stage's membership or uniqueness requirements; 
            `max_poule_size` is less than 3; or no official bout order exists for a generated poule size.
        RuntimeError
            If a generated poule has an unexpected number of matches.
        """
        self._validate_entries(entries, '_generate_poules')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleStage', '_generate_poules')

        poules = []

        num_entries = len(entries)
        poule_sizes = self._calculate_poule_sizes(num_entries, max_poule_size)

        entries_by_poule = self._assign_entries_to_poules(entries, poule_sizes)

        for poule_number, poule_entries in enumerate(entries_by_poule, start=1):
            poules.append(
                Poule(
                    poule_number = poule_number, 
                    stage_number = self.stage_number, 
                    entries = poule_entries,
                    score_to_win = self.score_to_win
                )
            )

        return tuple(poules)


    # --- Validation Helper Methods ---
    def _validate_poule_index(self, poule_index: int, method_name: str) -> None:
        """
        Validates that an index refers to a poule in this stage.

        Parameters
        ----------
        poule_index : int
            The zero-based poule index to validate.
        method_name : str
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is not a string or `poule_index` is not an integer.
        ValueError
            If `poule_index` is outside the valid range of poule indices.
        """
        if not isinstance(method_name, str):
            raise TypeError(f'method_name must be a string in PouleStage._validate_poule_index() - got {type(method_name).__name__}')

        validation.validate_int_in_range(poule_index, 0, self.num_poules - 1, 'Poule index', 'PouleStage', method_name)

    def _validate_entries(self, entries: tuple[TournamentEntry, ...], method_name: str | None = None) -> None:
        """
        Validate the provided entries.
        
        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries to validate.
        method_name : str | None, optional
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is neither a string nor `None`, `entries` is not a tuple, 
            an item is not a `TournamentEntry`.
        ValueError
            If fewer than two entries are provided, 
            an entry belongs to another tournament or appears more than once.
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
        Validate stage membership, uniqueness, and seeds for entries.

        The seeds must be exactly the integers from 1 through the number of entries, 
        but the entries do not need to be supplied in seed order.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            The seeded entries to validate.
        method_name : str | None, optional
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is neither a string nor `None`, `seeded_entries` is not a tuple, 
            an item is not a `SeededEntry`, or a seed is not an integer.
        ValueError
            If fewer than two entries are provided, 
            an entry belongs to another tournament or appears more than once, 
            a seed is missing, nonpositive, or repeated, 
            or the seeds are not exactly the integers from 1 through the number of entries.
        """
        # Validate location input
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in PouleStage._validate_seeded_entries() - got {type(method_name).__name__}')

        location = 'PouleStage' if method_name is None else f'PouleStage.{method_name}()'

        # Validate seeded entries provided
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
