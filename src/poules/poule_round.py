from dataclasses import dataclass, field

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.tournament_poule_results import TournamentPouleResults
from utils import snake_numbers


@dataclass(eq=False)
class PouleRound:
    """
    Represents one poule round in a tournament.

    A poule round validates and stores its entries in ascending initial-seed
    order, distributes each entry into exactly one poule using snake seeding,
    and coordinates match access and result calculation across those poules.
    Each entry fences every other entry in its assigned poule.
    
    Attributes
    ----------
    id : int
        The poule round's identifier within the tournament.
    tournament_id : int
        The identifier of the tournament containing the poule round.
    round_number : int
        The poule round's one-based position within the tournament.
    entries : tuple[TournamentEntry, ...]
        The entries assigned to the poule round. Each entry must belong to this tournament
        and have a unique initial seed from 1 through the number of entries. 
        Entries are stored in ascending initial-seed order, with seed 1 first.
    poules : tuple[Poule, ...]
        The generated poules in poule-number order.
    """
    id: int
    tournament_id: int
    round_number: int
    entries: tuple[TournamentEntry, ...]

    poules: tuple[Poule, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the round, sorts its entries by initial seed, and generates its poules.

        Raises
        ------
        TypeError
            If `id`, `tournament_id`, or `round_number` is not an integer;
            `entries` is not a tuple; an item is not a `TournamentEntry`; or an
            initial seed is not an integer.
        ValueError
            If `id`, `tournament_id`, or `round_number` is not positive; fewer
            than two entries are provided; an entry belongs to another
            tournament or appears more than once; an initial seed is missing,
            nonpositive, or repeated; or the initial seeds are not exactly the
            integers from 1 through the number of entries.
        """
        validation.validate_positive_int(self.id, 'PouleRound ID', 'PouleRound')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleRound')
        validation.validate_positive_int(self.round_number, 'Round Number', 'PouleRound')

        self._validate_entries(self.entries)

        self.entries = tuple(sorted(self.entries, key=lambda entry: entry.initial_seed))
        
        self.poules = self._generate_poules(self.entries)


    # --- Properties ---
    @property
    def num_poules(self) -> int:
        """Returns the number of poules in this round."""
        return len(self.poules)

    @property
    def num_entries(self) -> int:
        """Returns the number of entries in this round."""
        return len(self.entries)


    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Returns whether another object represents the same poule round."""
        if not isinstance(other, PouleRound):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id

    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Returns whether any poule in this round has started."""
        return any(poule.has_started() for poule in self.poules)

    def is_complete(self) -> bool:
        """Returns whether every poule in this round is complete."""
        return all(poule.is_complete() for poule in self.poules)
    

    # --- Poule Access Methods ---
    def get_poule_at(self, index: int) -> Poule:
        """
        Returns the poule at a specified index.
        
        Parameters
        ----------
        index : int
            The poule's zero-based position in the round.

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
        Returns a match from a specified poule.
        
        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the round.
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
        Returns the match that should currently be on piste in the specified poule.

        If a match in the poule is already in progress, it is returned. Otherwise,
        the first not-started match in the official bout order is returned.

        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the round.

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
        Returns the next match waiting to fence in the specified poule.

        The on-piste match is excluded, and the first remaining not-started 
        match in the official bout order is returned.
        
        Parameters
        ----------
        poule_index : int
            The poule's zero-based position in the round.

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
        Records the result of a specified match in a specified poule.

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
            If either index is outside its valid range, the match already has a
            forfeit result, or the scores do not form a valid completed result.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_match_result(match_index, score1, score2)

    def record_on_piste_match_result(self, poule_index: int, score1: int, score2: int) -> None:
        """
        Records the result of the on-piste match in a specified poule.

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
            If `poule_index` is outside its valid range, the match already has
            a forfeit result, or the scores do not form a valid completed result.
        RuntimeError
            If the poule is complete and therefore has no on-piste match.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_on_piste_match_result(score1, score2)


    # --- Result Calculation Methods ---
    def calculate_results(self, random_seed: int | None = None) -> TournamentPouleResults:
        """
        Calculates and returns a snapshot of the poule round's current results.

        The matches in each poule remain the source of truth. 
        Complete ranking ties are shuffled using `random_seed`.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order complete ranking ties. 
            If `None`, no fixed seed is used. Default is `None`.

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
        return TournamentPouleResults(self.tournament_id, self.poules, random_seed=random_seed)
    
    def calculate_ranked_results(self, random_seed: int | None = None) -> tuple[PouleEntryResult, ...]:
        """
        Calculates and returns the round's entry results in ranked order.

        Entries are ranked by victory ratio, indicator, and touches scored, all
        in descending order. Complete ties are shuffled using `random_seed`.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order complete ranking ties. 
            If `None`, no fixed seed is used. Default is `None`.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending ranking order.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return self.calculate_results(random_seed).round_results
    
    def calculate_ranked_results_display_names(self, random_seed: int | None = None) -> tuple[str, ...]:
        """
        Calculates and returns entry display names in round ranking order.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order complete ranking ties. 
            If `None`, no fixed seed is used. Default is `None`.

        Returns
        -------
        tuple[str, ...]
            The entries' display names in descending ranking order.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return self.calculate_results(random_seed).round_results_display_names


    # --- Creation Helper Methods ---
    def _calculate_poule_sizes(self, num_entries: int, max_poule_size: int = 7) -> tuple[int, ...]:
        """
        Calculates balanced poule sizes for a specified number of entries.

        The number of poules is minimized, no poule exceeds `max_poule_size`,
        and the poules differ in size by at most one.

        Parameters
        ----------
        num_entries : int
            The number of entries to distribute.
        max_poule_size : int, optional
            The maximum allowable poule size. Default is 7.

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
        validation.validate_int_at_least(num_entries, 2, 'num_entries', 'PouleRound', '_calculate_poule_sizes')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleRound', '_calculate_poule_sizes')

        # The minimal number of poules required is the smallest integer that 
        # satisfies the inequality: num_poules * max_poule_size >= num_entries
        num_poules = (num_entries + max_poule_size - 1) // max_poule_size # equivalent to ceil(num_entries / max_poule_size)

        integer_quotient, remainder = divmod(num_entries, num_poules)

        # Only a difference of one in poule size in poules is allowed upon round initialization
        larger_poule_size = integer_quotient + 1
        smaller_poule_size = integer_quotient

        num_larger_poules = remainder
        num_smaller_poules = num_poules - num_larger_poules

        return (larger_poule_size,) * num_larger_poules + (smaller_poule_size,) * num_smaller_poules

    def _assign_entries_to_poules(self, entries: tuple[TournamentEntry, ...], poule_sizes: tuple[int, ...]) -> tuple[tuple[TournamentEntry, ...], ...]:
        """
        Assigns entries to poules using snake distribution.

        Entries are assigned in their supplied order. This method therefore
        expects `entries` to already be in the intended seeding order.
        
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
            If `entries` is not a tuple; an item is not a `TournamentEntry`; an
            initial seed is not an integer; `poule_sizes` is not a tuple; or a
            poule size is not an integer.
        ValueError
            If `entries` violates the round's membership, uniqueness, or
            initial-seed requirements; `poule_sizes` is empty; a poule size is
            less than 2; or the poule sizes do not sum to the number of entries.
        """
        # Validate inputs
        self._validate_entries(entries, '_assign_entries_to_poules')
        
        if not isinstance(poule_sizes, tuple):
            raise TypeError(f'poule_sizes must be a tuple in PouleRound._assign_entries_to_poules() - got {type(poule_sizes).__name__}')

        if len(poule_sizes) < 1:
            raise ValueError(f'poule_sizes must contain at least 1 poule size in PouleRound._assign_entries_to_poules() - got {len(poule_sizes)}')

        for size in poule_sizes:
            validation.validate_int_at_least(size, 2, 'a poule size in poule_sizes', 'PouleRound', '_assign_entries_to_poules')

        if sum(poule_sizes) != len(entries):
            raise ValueError(f'The sum of poule_sizes must equal the number of entries in PouleRound._assign_entries_to_poules() - got sum={sum(poule_sizes)} and num_entries={len(entries)}')

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
        Generates the poules for a collection of entries.

        Entries are distributed in their supplied order, so they must already
        be ordered by ascending initial seed.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The validated entries in ascending initial-seed order.
        max_poule_size : int, optional
            The maximum allowable poule size. Default is 7.

        Returns
        -------
        tuple[Poule, ...]
            The generated poules in poule-number order.

        Raises
        ------
        TypeError
            If `entries` is not a tuple; an item is not a `TournamentEntry`; an
            initial seed is not an integer; or `max_poule_size` is not an
            integer.
        ValueError
            If `entries` violates the round's membership, uniqueness, or
            initial-seed requirements; `max_poule_size` is less than 3; or no
            official bout order exists for a generated poule size.
        RuntimeError
            If a generated poule has an unexpected number of matches.
        """
        self._validate_entries(entries, '_generate_poules')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleRound', '_generate_poules')

        poules = []

        num_entries = len(entries)
        poule_sizes = self._calculate_poule_sizes(num_entries, max_poule_size)

        entries_by_poule = self._assign_entries_to_poules(entries, poule_sizes)

        for poule_number, poule_entries in enumerate(entries_by_poule, start=1):
            poules.append(Poule(id=poule_number, tournament_id=self.tournament_id, poule_number=poule_number, entries=poule_entries))

        return tuple(poules)


    # --- Validation Helper Methods ---
    def _validate_poule_index(self, poule_index: int, method_name: str) -> None:
        """
        Validates that an index refers to a poule in this round.

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
            raise TypeError(f'method_name must be a string in PouleRound._validate_poule_index() - got {type(method_name).__name__}')

        validation.validate_int_in_range(poule_index, 0, self.num_poules - 1, 'poule index', 'PouleRound', method_name)

    def _validate_entries(self, entries: tuple[TournamentEntry, ...], method_name: str | None = None) -> None:
        """
        Validates round membership, uniqueness, and initial seeds for entries.

        The initial seeds must be exactly the integers from 1 through the
        number of entries, but the entries do not need to be supplied in seed order.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The tournament entries to validate.
        method_name : str | None, optional
            The name of the method requesting the validation. 
            If `None`, error messages identify `PouleRound` without naming 
            a specific method. Default is `None`.

        Raises
        ------
        TypeError
            If `method_name` is neither a string nor `None`, 
            `entries` is not a tuple, an item is not a `TournamentEntry`, 
            or an initial seed is not an integer.
        ValueError
            If fewer than two entries are provided, an entry belongs to another
            tournament or appears more than once, an initial seed is missing,
            nonpositive, or repeated, or the initial seeds are not exactly the
            integers from 1 through the number of entries.
        """
        # Validate location input
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in PouleRound._validate_entries() - got {type(method_name).__name__}')

        location = 'PouleRound' if method_name is None else f'PouleRound.{method_name}()'

        # Validate entries
        if not isinstance(entries, tuple):
            raise TypeError(f'Entries must be a tuple in {location} - got {type(entries).__name__}')

        if len(entries) < 2:
            raise ValueError(f'Entries must contain at least 2 entries in {location} - got {len(entries)}')

        # Validate each entry
        seen_entry_ids: set[int] = set()
        seen_initial_seeds: set[int] = set()

        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Entry at index {i} in {location} must be a TournamentEntry - got {type(entry).__name__}')
            
            if self.tournament_id != entry.tournament_id:
                raise ValueError(f'Entry {entry.id} at index {i} in {location} has tournament ID {entry.tournament_id}, '
                                 f'which does not match the poule round\'s tournament ID {self.tournament_id}')
            
            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry {entry.id} exists more than once in entries in {location}')
            
            initial_seed = entry.initial_seed

            if initial_seed is None:
                raise ValueError(f'Entry {entry.id} at index {i} in {location} must have an initial seed')

            validation.validate_positive_int(initial_seed, f'Initial seed for entry {entry.id} at index {i}', 'PouleRound', method_name)

            if initial_seed in seen_initial_seeds:
                raise ValueError(f'Initial seed {initial_seed} is assigned more than once in {location}')
            
            seen_entry_ids.add(entry.id)
            seen_initial_seeds.add(initial_seed)

        # Verify that all expected initial seeds are present
        expected_initial_seeds = set(range(1, len(entries) + 1))

        if seen_initial_seeds != expected_initial_seeds:
            raise ValueError(f'Initial seeds in {location} must be a one-to-one mapping with the integers from 1 through {len(entries)}')
