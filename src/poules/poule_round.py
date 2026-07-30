import math

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
    Represents a stage in a tournament where entries fence each other in one 
    or more poules. All entries in a poule round get placed into exactly one poule, 
    and each entry fences every other entry in their poule.

    This class acts as a controller for all the poules in this poule round.
    
    Attributes
    ----------
    id : int
        The unique identifier of the poule round.
    tournament_id : int
        The unique identifier of the tournament that the poule round belongs in.
    round_number : int
        The one-based round number of the poule round in the tournament.
    entries : tuple[TournamentEntry, ...]
        The tournament entries assigned to the poule round, ordered from
        highest to lowest initial seed. This order determines their snake
        distribution among the poules.
    
    poules : tuple[Poule, ...], init=False
        The poules that belong in this poule round.
    """
    id: int
    tournament_id: int
    round_number: int
    entries: tuple[TournamentEntry, ...]

    poules: tuple[Poule, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the ID, tournament ID, round number, and entries, and generates the poules from the entries.

        Raises
        ------
        TypeError
            If ID, tournament ID, or round number is not an integer, if entries is not a tuple, or if any entry is not a TournamentEntry object.
        ValueError
            If ID, tournament ID, or round number is not positive, if entries contains fewer than 2 entries, or if any entry's tournament ID does not match the
            poule round's tournament ID, or if any entry occurs more than once.
        """
        validation.validate_positive_int(self.id, 'PouleRound ID', 'PouleRound')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleRound')
        validation.validate_positive_int(self.round_number, 'Round Number', 'PouleRound')

        self._validate_entries(self.entries, '__post_init__')

        self.entries = tuple(sorted(self.entries, key=lambda entry: entry.initial_seed))
        
        self.poules = self._generate_poules(self.entries)


    # --- Properties ---
    @property
    def num_poules(self) -> int:
        """Returns the number of poules in the round."""
        return len(self.poules)

    @property
    def num_entries(self) -> int:
        """Returns the number of entries in the round."""
        return len(self.entries)


    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Checks whether two PouleRound objects are equal based on their ID and tournament ID."""
        if not isinstance(other, PouleRound):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id

    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Returns whether the poule round has started yet or not - true if any poule in the round has started."""
        return any(poule.has_started() for poule in self.poules)

    def is_complete(self) -> bool:
        """Checks whether the poule round is complete - true if all the poules in the round are complete."""
        return all(poule.is_complete() for poule in self.poules)
    

    # --- Poule Access Methods ---
    def get_poule_at(self, index: int) -> Poule:
        """
        Returns the poule at the specified index.
        
        Parameters
        ----------
        index : int
            The index of the poule to retrieve.

        Returns
        -------
        Poule
            The poule at the specified index.

        Raises
        ------
        TypeError
            If the index is not an integer.
        ValueError
            If the index is outside the valid poule range: 0 to (number of poules - 1).
        """
        self._validate_poule_index(index, 'get_poule_at')
        return self.poules[index]
    
    def get_match_at(self, poule_index: int, match_index: int) -> PouleMatch:
        """
        Returns the poule match at the specified poule and match index.
        
        Parameters
        ----------
        poule_index : int
            The index of the poule to retrieve the match from.
        match_index : int
            The index of the match to retrieve from the specified poule.

        Returns
        -------
        PouleMatch
            The match at the specified poule and match index.

        Raises
        ------
        TypeError
            If either index is not an integer.
        ValueError
            If either index is outside its valid range.
            Poule index must be between 0 and (number of poules - 1).
            Match index must be between 0 and (number of matches in the poule - 1).
        """
        self._validate_poule_index(poule_index, 'get_match_at')
        return self.poules[poule_index].get_match_at(match_index)

    def get_on_piste_match(self, poule_index: int) -> PouleMatch | None:
        """
        Returns the match that should currently be on piste in the specified poule.

        If a match in the poule is already in progress, it is returned. Otherwise,
        the first incomplete match in the official bout order is returned.

        Parameters
        ----------
        poule_index : int
            The zero-based index of the poule.

        Returns
        -------
        PouleMatch | None
            The match that should be on piste, or None if the poule is complete.

        Raises
        ------
        TypeError
            If the poule index is not an integer.
        ValueError
            If the poule index is outside the valid range.
        """
        self._validate_poule_index(poule_index, 'get_on_piste_match')
        return self.poules[poule_index].get_on_piste_match()

    def get_on_deck_match(self, poule_index: int) -> PouleMatch | None:
        """
        Returns the next match waiting to fence in the specified poule.

        The on-piste match is excluded, and the first remaining not-started match
        in the official bout order is returned.
        
        Parameters
        ----------
        poule_index : int
            The index of the poule to retrieve the "on-deck" match from.

        Returns
        -------
        PouleMatch | None
            The "on-deck" match at the specified poule, or None if there is no match on deck.

        Raises
        ------
        TypeError
            If the poule index is not an integer.
        ValueError
            If the poule index is outside the valid poule range: 0 to (number of poules - 1).
        """
        self._validate_poule_index(poule_index, 'get_on_deck_match')
        return self.poules[poule_index].get_on_deck_match()
    

    # --- Match Result Recording Methods ---
    def record_match_result(self, poule_index: int, match_index: int, score1: int, score2: int) -> None:
        """
        Records a result for a specified match in a specified poule.

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
            If either index or score is not an integer.
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
            If the poule index or either score is not an integer.
        ValueError
            If the poule index is outside its valid range, the match already has a
            forfeit result, or the scores do not form a valid completed result.
        RuntimeError
            If the poule is complete and therefore has no on-piste match.
        """
        poule = self.get_poule_at(poule_index)
        poule.record_on_piste_match_result(score1, score2)


    # --- Result Calculation Methods ---
    def calculate_results(self, random_seed: int | None = None) -> TournamentPouleResults:
        """
        Calculates and returns a snapshot of the poule round's current results.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to resolve complete ranking ties. If None, complete ties
            are resolved nondeterministically. Default is None.

        Returns
        -------
        TournamentPouleResults
            A newly calculated snapshot of the results across all poules.

        Raises
        ------
        TypeError
            If random_seed is neither an integer nor None.
        ValueError
            If random_seed is negative.
        """
        return TournamentPouleResults(self.tournament_id, self.poules, random_seed=random_seed)
    
    def calculate_ranked_results(self, random_seed: int | None = None) -> tuple[PouleEntryResult, ...]:
        """
        Calculates and returns the round's entry results in ranked order.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to resolve complete ranking ties. If None, complete ties
            are resolved nondeterministically. Default is None.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending ranking order.

        Raises
        ------
        TypeError
            If random_seed is neither an integer nor None.
        ValueError
            If random_seed is negative.
        """
        return self.calculate_results(random_seed).round_results
    
    def calculate_ranked_results_display_names(self, random_seed: int | None = None) -> tuple[str, ...]:
        """
        Calculates and returns the display names in round ranking order.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to resolve complete ranking ties. If None, complete ties
            are resolved nondeterministically. Default is None.

        Returns
        -------
        tuple[str, ...]
            The entries' display names in descending ranking order.

        Raises
        ------
        TypeError
            If random_seed is neither an integer nor None.
        ValueError
            If random_seed is negative.
        """
        return self.calculate_results(random_seed).round_results_display_names


    # --- Creation Helper Methods ---
    def _calculate_poule_sizes(self, num_entries: int, max_poule_size: int = 7) -> tuple[int, ...]:
        """
        Calculates the number of poules that there should be and their respective sizes 
        based on the number of entries in the poule round and the maximum allowable poule size.
        The poule sizes must be such that all poules differ in size by at most one, and the number of poules is minimized.

        Parameters
        ----------
        num_entries : int
            The number of entries in the PouleRound.
        max_poule_size : int
            The maximum allowable size for the poules.

        Returns
        -------
        tuple[int, ...]
            A tuple of integers where the size of the tuple is the number of poules in the round and the 
            integer values represent the size of each poule.

        Raises
        ------
        TypeError
            If num_entries or max_poule_size is not an integer.
        ValueError
            If num_entries is less than 2 or max_poule_size is less than 3.
        RuntimeError
            If a valid configuration of poule sizes cannot be found for the given inputs.
        """
        validation.validate_int_at_least(num_entries, 2, 'num_entries', 'PouleRound', '_calculate_poule_sizes')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleRound', '_calculate_poule_sizes')

        # Check if only one poule is necessary
        if num_entries <= max_poule_size:
            return (num_entries,)

        # Idea: Try higher priority candidate poule sizes first
        min_size = (max_poule_size + 1) // 2 # The minimum possible size
        current_max_size = max_poule_size

        while current_max_size >= min_size:
            # Case 1: Evenly divisible
            if num_entries % current_max_size == 0:
                return (current_max_size,) * (num_entries // current_max_size)
            
            # Case 2: Can form with combination of size and size-1
            num_poules = int(math.ceil(num_entries / current_max_size))
            if num_entries > num_poules * (current_max_size - 1):
                sizes = [current_max_size] * num_poules
                i = -1
                while abs(i) <= len(sizes) and sum(sizes) != num_entries:
                    sizes[i] = current_max_size-1
                    i-=1
                if sum(sizes) == num_entries:
                    return tuple(sizes)
                else:
                    raise RuntimeError(f'Could not obtain the poule sizes configuration in PouleRound._calculate_poule_sizes()')
            
            # Case 3: Cannot form with this size; try next priority size
            current_max_size -= 1

        raise RuntimeError('Could not find a solution in PouleRound._calculate_poule_sizes()')    
    

    def _assign_entries_to_poules(self, entries: tuple[TournamentEntry, ...], poule_sizes: tuple[int, ...]) -> tuple[tuple[TournamentEntry, ...], ...]:
        """
        Returns a tuple of tuples of entries that represent the entries in each poule.
        
        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries to distribute into poules.
        poule_sizes : tuple[int, ...]
            The sizes of each poule.

        Returns
        -------
        tuple[tuple[TournamentEntry, ...], ...]
            The entries for each poule in the poule round, distributed in a "snake" pattern.

        Raises
        ------
        TypeError
            If entries is not a tuple, 
            if any entry is not a TournamentEntry object, 
            if poule_sizes is not a tuple, 
            or if any poule size is not an integer.
        ValueError
            If entries contains less than 2 entries, 
            if any entry's tournament ID does not match the poule round's tournament ID,
            if poule_sizes contains less than 1 poule size, 
            if the sum of poule_sizes does not equal the number of entries, 
            if any poule size is less than 2,
            or if any entry appears more than once in entries.
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
        Generates the poules from the given input entries.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries to distribute into poules.
        max_poule_size : int, default=7
            The maximum allowable size for any poule.

        Returns
        -------
        tuple[Poule, ...]
            The poules belonging to this poule round.

        Raises
        ------
        TypeError
            If entries is not a tuple, if any entry is not a TournamentEntry object, or if max_poule_size is not an integer.
        ValueError
            If entries contains less than 2 entries, or if max_size is less than 3, or if any entry's tournament ID does not match the poule round's tournament ID.
        """
        self._validate_entries(entries, '_generate_poules')
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', 'PouleRound', '_generate_poules')

        poules = []

        n = len(entries)
        poule_sizes = self._calculate_poule_sizes(n, max_poule_size)

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

    def _validate_entries(self, entries: tuple[TournamentEntry, ...], method_name: str) -> None:
        """
        Validates the entries assigned to this poule round.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The tournament entries to validate.
        method_name : str
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is not a string, `entries` is not a tuple, or
            an item in `entries` is not a TournamentEntry object.
        ValueError
            If fewer than two entries are provided, an entry belongs to another
            tournament, or an entry appears more than once.
        """
        if not isinstance(method_name, str):
            raise TypeError(f'method_name must be a string in PouleRound._validate_entries() - got {type(method_name).__name__}')

        location = f'PouleRound.{method_name}()'

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

            validation.validate_positive_int(initial_seed, f'Initial seed for entry {entry.id} at index {i}', 'PouleRound', '_validate_entries')

            if initial_seed in seen_initial_seeds:
                raise ValueError(f'Initial seed {initial_seed} is assigned more than once in {location}')
            
            seen_entry_ids.add(entry.id)
            seen_initial_seeds.add(entry.initial_seed)

        # Verify that all expected initial seeds are present
        expected_initial_seeds = set(range(1, len(entries) + 1))

        if seen_initial_seeds != expected_initial_seeds:
            raise ValueError(f'Initial seeds in {location} must be a one-to-one mapping '
                             f'with the integers from 1 through {len(entries)}')
