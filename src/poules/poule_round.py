from dataclasses import dataclass, field

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule import Poule
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_round_results import PouleRoundResults
from utils import snake_numbers


@dataclass(eq=False)
class PouleRound:
    """
    Represent a round in a poule stage.

    A poule round distributes each entry into exactly one poule using snake seeding,
    and coordinates match access and result calculation across those poules.
    
    Attributes
    ----------
    round_number : int
        The poule round's one-based position within the stage.
    stage_number : int
        The poule stage's one-based position within the tournament this round belongs to.
    entries : tuple[TournamentEntry, ...]
        The entries in round-seed order, with the highest-ranked entry first.
        Tuple position determines the round seed: index 0 represents seed 1.
        Entries must belong to the same tournament and have unique entry IDs.
        The supplied order is preserved.
    score_to_win : int, default=5
        The target score and maximum permitted recorded score for either entry.
    poules : tuple[Poule, ...]
        The generated poules in poule-number order.
    """
    round_number: int
    stage_number: int
    entries: tuple[TournamentEntry, ...]

    score_to_win: int = field(default=5, kw_only=True)
    poules: tuple[Poule, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validate the round configuration and entries, then generate its poules.

        The supplied entry order determines the round seeds and is preserved.
        Entries are distributed into balanced poules using snake seeding.

        Raises
        ------
        TypeError
            If `round_number`, `stage_number`, or `score_to_win` is not an integer,
            if `entries` is not a tuple, or if an item is not a `TournamentEntry`.
        ValueError
            If `round_number`, `stage_number`, or `score_to_win` is not positive,
            if fewer than two entries are provided, if the entries do not share a tournament ID, 
            or if an entry ID or fencer ID occurs more than once.
        """
        location = 'PouleRound'

        validation.validate_positive_int(self.stage_number, 'Stage number', location)
        validation.validate_positive_int(self.round_number, 'Round number', location)
        validation.validate_positive_int(self.score_to_win, 'Score to win', location)

        self.poules = self._generate_poules(self.entries)


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the poule round."""
        return (
            f'PouleRound in round {self.round_number} of stage {self.stage_number} in tournament {self.tournament_id}'
        )

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the entries in this round."""
        return self.entries[0].tournament_id

    @property
    def num_poules(self) -> int:
        """Return the number of poules in this round."""
        return len(self.poules)

    @property
    def num_entries(self) -> int:
        """Return the number of entries in this round."""
        return len(self.entries)


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """Return whether another object represents the same poule round."""
        if not isinstance(other, PouleRound):
            return False

        return (
            self.round_number == other.round_number and 
            self.stage_number == other.stage_number and
            self.tournament_id == other.tournament_id
        )


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Return whether any poule in this round has started."""
        return any(poule.has_started() for poule in self.poules)

    def is_complete(self) -> bool:
        """Return whether every poule in this round is complete."""
        return all(poule.is_complete() for poule in self.poules)

    def is_incomplete(self) -> bool:
        """Return whether any poule in this round is incomplete."""
        return not self.is_complete()


    # --- Poule Access Methods ---
    def get_poule_at(self, index: int) -> Poule:
        """
        Return the poule at a specified index.
        
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
        Return a match from a specified poule.
        
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
        Return the match that should currently be on piste in the specified poule.

        The first incomplete match in the official bout order is returned.

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
        Return the next match waiting to fence in the specified poule.

        The on-piste match is excluded, 
        and the first remaining incomplete match in the official bout order is returned.
        
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
    def record_match_score(self, poule_index: int, match_index: int, score1: int, score2: int) -> None:
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
        self.get_poule_at(poule_index).record_match_score(match_index, score1, score2)

    def record_on_piste_match_score(self, poule_index: int, score1: int, score2: int) -> None:
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
        self.get_poule_at(poule_index).record_on_piste_match_score(score1, score2)

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
        self.get_poule_at(poule_index).replace_with_score(match_index, score1, score2)

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
        self.get_poule_at(poule_index).record_forfeit(match_index, forfeiting_index)

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
        self.get_poule_at(poule_index).replace_with_forfeit(match_index, forfeiting_index)


    # --- Result Calculation Methods ---
    def calculate_results(self, random_seed: int | None = None) -> PouleRoundResults:
        """
        Calculate and return a snapshot of the poule round's current results.

        The matches in each poule remain the source of truth. 
        Complete ranking ties are shuffled using `random_seed`.

        Parameters
        ----------
        random_seed : int | None, optional
            The seed used to order ranking ties. 

        Returns
        -------
        PouleRoundResults
            A newly calculated snapshot of the results across all poules in the round.

        Raises
        ------
        TypeError
            If `random_seed` is neither an integer nor `None`.
        ValueError
            If `random_seed` is negative.
        """
        return PouleRoundResults(self.poules, random_seed)

    def calculate_results_flattened(self) -> tuple[PouleEntryResult, ...]:
        """
        Calculate and return the round's entry results without ranking them.

        Only completed matches contribute to the statistics.
        The round does not need to be complete.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            Newly calculated entry result snapshots in poule order,
            preserving the entry order within each poule.
        """
        return self.calculate_results().poule_results_flattened

    def calculate_ranked_results(self, random_seed: int | None = None) -> tuple[PouleEntryResult, ...]:
        """
        Calculate and return the round's entry results in ranked order.

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
        return self.calculate_results(random_seed).round_results

    def calculate_ranked_results_display_names(self, random_seed: int | None = None) -> tuple[str, ...]:
        """
        Calculate and return entry display names in round ranking order.

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
        return self.calculate_results(random_seed).round_results_display_names


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
        class_location, method_location = 'PouleRound', '_calculate_poule_sizes'
        validation.validate_int_at_least(num_entries, 2, 'num_entries', class_location, method_location)
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', class_location, method_location)

        # The minimal number of poules required is the smallest integer that satisfies 
        # the inequality: num_poules * max_poule_size >= num_entries
        num_poules = (num_entries + max_poule_size - 1) // max_poule_size # equivalent to ceil(num_entries / max_poule_size)

        integer_quotient, remainder = divmod(num_entries, num_poules)

        # Only a difference of one in poule size in poules is allowed upon round initialization
        larger_poule_size = integer_quotient + 1
        smaller_poule_size = integer_quotient

        num_larger_poules = remainder
        num_smaller_poules = num_poules - num_larger_poules

        return (larger_poule_size,) * num_larger_poules + (smaller_poule_size,) * num_smaller_poules

    def _assign_entries_to_poules(self, entries: tuple[TournamentEntry, ...], 
                                  poule_sizes: tuple[int, ...]) -> tuple[tuple[TournamentEntry, ...], ...]:
        """
        Distribute previously validated entries into poules using snake seeding.

        Entries are processed in their supplied round-seed order, with the highest-ranked entry first. 
        Poules that have reached their target size are skipped. 
        This method does not validate the entries themselves.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The previously validated entries in round-seed order.
        poule_sizes : tuple[int, ...]
            The target size of each poule in poule-index order.

        Returns
        -------
        tuple[tuple[TournamentEntry, ...], ...]
            The entries assigned to each poule in poule-index order.
            Entries within each poule retain their assignment order.

        Raises
        ------
        TypeError
            If `poule_sizes` is not a tuple or a poule size is not an integer.
        ValueError
            If `poule_sizes` is empty, if a poule size is less than 2,
            or if the poule sizes do not sum to the number of entries.
        """
        class_location, method_location = 'PouleRound', '_assign_entries_to_poules'
        location = f'{class_location}.{method_location}()'

        # Validate inputs
        if not isinstance(poule_sizes, tuple):
            raise TypeError(
                f'poule_sizes must be a tuple in {location} - got {type(poule_sizes).__name__}'
            )

        if not poule_sizes:
            raise ValueError(
                f'poule_sizes must contain at least 1 poule size in {location} - got {len(poule_sizes)}'
            )

        for size in poule_sizes:
            validation.validate_int_at_least(size, 2, 'a poule size in poule_sizes', class_location, method_location)

        if sum(poule_sizes) != len(entries):
            raise ValueError(
                f'The sum of poule_sizes must equal the number of entries in {location} '
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
        Validate the entries and generate balanced poules using snake seeding.

        The supplied entry order defines the round seeds, with the highest-ranked entry first. 
        Entries are not sorted by this method.
        Each generated poule receives this round's round number, stage number, and score to win.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries in round-seed order.
        max_poule_size : int, optional, default=7
            The maximum allowable poule size. Must be at least 3.

        Returns
        -------
        tuple[Poule, ...]
            The generated poules in poule-number order, numbered from 1.

        Raises
        ------
        TypeError
            If `entries` is not a tuple, if an item is not a `TournamentEntry`,
            or if `max_poule_size` is not an integer.
        ValueError
            If fewer than two entries are provided, if the entries do not share a tournament ID, 
            if an entry ID or fencer ID occurs more than once, if `max_poule_size` is less than 3, 
            or if no official bout order exists for a generated poule size.
        RuntimeError
            If a generated poule has an unexpected number of matches.
        """
        class_location, method_location = 'PouleRound', '_generate_poules'
        self._validate_entries(entries, method_location)
        validation.validate_int_at_least(max_poule_size, 3, 'max_poule_size', class_location, method_location)

        poules = []

        num_entries = len(entries)
        poule_sizes = self._calculate_poule_sizes(num_entries, max_poule_size)

        entries_by_poule = self._assign_entries_to_poules(entries, poule_sizes)

        for poule_number, poule_entries in enumerate(entries_by_poule, start=1):
            poules.append(
                Poule(
                    poule_number=poule_number,
                    round_number=self.round_number,
                    stage_number=self.stage_number,
                    entries=poule_entries,
                    score_to_win=self.score_to_win
                )
            )

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
        class_name = 'PouleRound'
        if not isinstance(method_name, str):
            raise TypeError(f'method_name must be a string in {class_name}._validate_poule_index() - got {type(method_name).__name__}')

        validation.validate_int_in_range(poule_index, 0, self.num_poules - 1, 'Poule index', class_name, method_name)

    def _validate_entries(self, entries: tuple[TournamentEntry, ...], method_name: str | None = None) -> None:
        """
        Validate entry types, minimum count, shared tournament, and uniqueness.

        The expected tournament ID is taken from the first entry after its type has been checked. 
        Entry uniqueness is determined by entry ID.
        The supplied order is neither changed nor checked against a ranking.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries to validate.
        method_name : str | None, optional
            The method name to include in validation error messages.

        Raises
        ------
        TypeError
            If `method_name` is neither a string nor `None`,
            if `entries` is not a tuple, or if an item is not a `TournamentEntry`.
        ValueError
            If fewer than two entries are provided, 
            if an entry's tournament ID differs from the first entry's tournament ID, 
            or if an entry ID or fencer ID occurs more than once.
        """
        class_name = 'PouleRound'

        # Validate location input
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(
                f'method_name must be either a string or None in {class_name}._validate_entries() '
                f'- got {type(method_name).__name__}'
            )

        location = class_name if method_name is None else f'{class_name}.{method_name}()'

        # Validate entries
        if not isinstance(entries, tuple):
            raise TypeError(f'Entries must be a tuple in {location} - got {type(entries).__name__}')

        if len(entries) < 2:
            raise ValueError(f'Entries must contain at least 2 entries in {location} - got {len(entries)}')

        # Validate each entry
        seen_entry_ids: set[int] = set()
        seen_fencer_ids: set[int] = set()

        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Entry at index {i} in {location} must be a TournamentEntry - got {type(entry).__name__}')

            if i == 0:
                tournament_id = entry.tournament_id

            if entry.tournament_id != tournament_id:
                raise ValueError(
                    f'Entry {entry.id} at index {i} in {location} has tournament ID {entry.tournament_id}, '
                    f'which does not match the first entry\'s tournament ID {tournament_id}'
                )

            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry {entry.id} exists more than once in entries in {location}')

            if entry.fencer.id in seen_fencer_ids:
                raise ValueError(f'Fencer {entry.fencer.id} exists more than once in entries in {location}')

            seen_entry_ids.add(entry.id)
            seen_fencer_ids.add(entry.fencer.id)
