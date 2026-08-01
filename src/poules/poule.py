from collections.abc import Iterable
from dataclasses import dataclass, field

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule_orders import POULE_BOUT_ORDER
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_result import PouleResult


@dataclass(eq=False)
class Poule:
    """
    Represents a poule and its ordered matches within a tournament.

    The order of `entries` determines each entry's fencer number in the poule.
    The matches are automatically generated using the official bout order.

    Attributes
    ----------
    id : int
        The poule's unique identifier.
    tournament_id : int
        The identifier of the tournament containing the poule.
    poule_number : int
        The poule's number within the poule round.
    entries : tuple[TournamentEntry, ...]
        The tournament entries in fencer-number order.
    matches : tuple[PouleMatch, ...]
        The poule matches in official bout order.
    """
    id: int
    tournament_id: int
    poule_number: int
    entries: tuple[TournamentEntry, ...]
    matches: tuple[PouleMatch, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validates the poule and generates its ordered match schedule.

        Raises
        ------
        TypeError
            If an ID or the poule number is not an integer, `entries` is not
            iterable, or an item is not a `TournamentEntry` object.
        ValueError
            If an ID or the poule number is not positive, fewer than two entries
            are provided, an entry is repeated or belongs to another tournament,
            or no bout order exists for the poule size.
        RuntimeError
            If the generated schedule has the wrong number of matches.
        """
        # Validate the ID and integer parameters
        validation.validate_positive_int(self.id, 'ID', 'Poule')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'Poule')
        validation.validate_positive_int(self.poule_number, 'Poule number', 'Poule')

        # Allow the entries input to be an iterable object
        if not isinstance(self.entries, Iterable):
            raise TypeError(f'Entries must be an iterable - got {type(self.entries).__name__}')

        # Store entries as a tuple to prevent accidental membership or order changes.
        self.entries = tuple(self.entries)
                
        # Validate the entries provided and generate the poule matches given the validated entries
        self.matches = self._generate_matches(self.entries)

        # Check that the correct number of matches was produced
        expected_number_matches = self.size * (self.size - 1) // 2

        if self.number_matches != expected_number_matches:
            raise RuntimeError(f'Poule {self.id} generated {self.number_matches} matches, '
                               f'but {expected_number_matches} matches were expected.')


    # --- Properties ---
    @property
    def size(self) -> int:
        """Returns the number of entries in the poule."""
        return len(self.entries)

    @property
    def number_matches(self) -> int:
        """Returns the number of matches in the poule."""
        return len(self.matches)
    

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Returns whether another object represents the same poule."""
        if not isinstance(other, Poule):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Returns whether any match in the poule is in progress or complete."""
        return any(match.is_in_progress() or match.is_complete() for match in self.matches)

    def is_complete(self) -> bool:
        """Returns whether every scheduled match in the poule is complete."""
        return all(match.is_complete() for match in self.matches)
    
    def has_entry(self, entry: TournamentEntry) -> bool:
        """Returns True if the poule has this tournament entry; otherwise False."""
        self._validate_entry(entry)
        return entry in self.entries


    # --- Match Access Methods ---
    def get_match_at(self, index: int) -> PouleMatch:
        """
        Gets a poule match at a specified index.
        
        Parameters
        ----------
        index : int
            The match's zero-based position in the official bout order.

        Returns
        -------
        PouleMatch
            The poule match at the index.

        Raises
        ------
        TypeError
            If the index is not an integer.
        ValueError
            If the index is outside of the valid range of match indices.
        """
        self._validate_match_index(index, 'get_match_at')
        return self.matches[index]

    def get_on_piste_match(self) -> PouleMatch | None:
        """
        Returns the match that should currently be on piste.

        If a match is in progress, it is returned. Otherwise, the first
        not-started match in the official bout order is returned.

        Returns
        -------
        PouleMatch | None
            The match that should be on piste, or None if the poule is complete.

        Notes
        -----
        This method assumes that the poule is being run one match at a time on
        one piste. It is not intended for double-stripping.
        """
        in_progress_match = next((match for match in self.matches if match.is_in_progress()), None)

        if in_progress_match is None:
            return next((match for match in self.matches if match.is_incomplete()), None)
        
        return in_progress_match

    def get_on_deck_match(self) -> PouleMatch | None:
        """
        Returns the next match waiting to fence.

        The on-piste match is excluded, and the first remaining not-started
        match in the official bout order is returned.

        Returns
        -------
        PouleMatch | None
            The match on deck, or None if no match is waiting to fence.
        """
        on_piste_match = self.get_on_piste_match()

        if on_piste_match is None:
            return None

        return next((match for match in self.matches if match is not on_piste_match and match.has_not_started()), None)


    # --- Match Result Recording Methods ---
    def record_match_result(self, index: int, score1: int, score2: int) -> None:
        """
        Records the result of a specified match.

        Parameters
        ----------
        index : int
            The match's zero-based position in the official bout order.
        score1 : int
            The score to record for the first entry in the match.
        score2 : int
            The score to record for the second entry in the match.

        Raises
        ------
        TypeError
            If the index or either score is not an integer.
        ValueError
            If the index is outside the valid range, the match already has a
            forfeit result, or the scores do not form a valid completed result.
        """
        match = self.get_match_at(index)
        match.record_score(score1, score2)

    def record_on_piste_match_result(self, score1: int, score2: int) -> None:
        """
        Records the result of the current on-piste match.

        Parameters
        ----------
        score1 : int
            The score to record for the first entry in the match.
        score2 : int
            The score to record for the second entry in the match.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If the match already has a forfeit result or the scores do not form
            a valid completed result.
        RuntimeError
            If the poule is complete and there is no on-piste match.
        """
        match = self.get_on_piste_match()
        
        if match is None:
            raise RuntimeError(f'Poule {self.id} is already complete.')

        match.record_score(score1, score2)


    # --- Result Calculation Methods ---
    def calculate_results(self) -> PouleResult:
        """
        Calculates and returns a snapshot of the poule's current results.
        
        The matches remain the source of truth for all results.
        """
        return PouleResult(self.entries, self.matches, self.id, self.tournament_id)

    def calculate_ranked_results(self) -> tuple[PouleEntryResult, ...]:
        """Calculates and returns the poule's entry results in ranked order."""
        poule_result = self.calculate_results()
        return poule_result.ranked_results

    def calculate_ranked_results_display_names(self) -> tuple[str, ...]:
        """Returns the entries' display names in current poule ranking order."""
        poule_result = self.calculate_results()
        return poule_result.ranked_results_display_names


    # --- Match Generation Helper Methods ---
    def _create_match(self, match_id: int, match_index: int, match_pair: tuple[int, int], entries: tuple[TournamentEntry, ...]) -> PouleMatch:
        """
        Creates one poule match from a pair in the official bout order.

        The match pair contains one-based fencer numbers. Fencer number `i`
        refers to the entry at index `i - 1`.

        Parameters
        ----------
        match_id : int
            The match's identifier within this poule.
        match_index : int
            The match's zero-based position in the official bout order.
        match_pair : tuple[int, int]
            A pair of one-based fencer numbers from the official bout order.
        entries : tuple[TournamentEntry, ...]
            The validated entries in fencer-number order.

        Returns
        -------
        PouleMatch
            A generated poule match based on the supplied match information.

        Raises
        ------
        TypeError
            If `match_id`, `match_index`, or either fencer number is not an
            integer, or if `match_pair` is not a tuple.
        ValueError
            If `match_id` is not positive, `match_index` or a fencer number is
            outside the valid range, `match_pair` does not contain exactly two
            fencer numbers, or the two fencer numbers are the same.
        RuntimeError
            If the match pair selects the same entry twice despite using two
            different fencer numbers.
        """
        number_matches = len(entries) * (len(entries) - 1) // 2

        validation.validate_positive_int(match_id, 'match_id', 'Poule', '_create_match')
        validation.validate_int_in_range(match_index, 0, number_matches - 1, 'match_index', 'Poule', '_create_match')

        self._validate_match_pair(match_pair, entries, '_create_match')

        # Get entries from which to create the match
        fencer_number1, fencer_number2 = match_pair

        entry1 = entries[fencer_number1 - 1]
        entry2 = entries[fencer_number2 - 1]

        # Check that the entries are distinct
        if entry1 == entry2:
            raise RuntimeError('Poule._create_match() selected the same entry twice. '
                               'This should not be possible after the entries and match pair have been validated.')

        # Create and return the generated poule match
        return PouleMatch(id=match_id, tournament_id=self.tournament_id, entry1=entry1, entry2=entry2, poule_id=self.id, match_index=match_index)

    def _generate_matches(self, entries: tuple[TournamentEntry, ...]) -> tuple[PouleMatch, ...]:
        """
        Validates the entries and generates their official match schedule.

        The supplied entry order determines which TournamentEntry objects correspond
        to the one-based fencer numbers used by the standard bout order.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries for which to generate a fresh poule match schedule.

        Returns
        -------
        tuple[PouleMatch, ...]
            Newly created poule matches in official bout order.

        Raises
        ------
        TypeError
            If `entries` is not a tuple, or if an item is not a
            `TournamentEntry` object.
        ValueError
            If fewer than two entries are provided, an entry is repeated or
            belongs to another tournament, or no bout order exists for the
            poule size.
        """
        self._validate_entries(entries)
        
        match_schedule_order = POULE_BOUT_ORDER[len(entries)]

        return tuple(self._create_match(index + 1, index, match_pair, entries) for index, match_pair in enumerate(match_schedule_order))


    # --- Validation Helper Methods ---
    def _validate_match_index(self, index: int, method_name: str) -> None:
        """
        Validates that an index refers to a match in this poule.

        Parameters
        ----------
        index : int
            The zero-based match index to validate.
        method_name : str
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is not a string or `index` is not an integer.
        ValueError
            If `index` is outside the valid range of match indices.
        """
        if not isinstance(method_name, str):
            raise TypeError(f'method_name must be a string in Poule._validate_match_index() - got {type(method_name).__name__}')

        validation.validate_int_in_range(index, 0, self.number_matches - 1, 'index', 'Poule', method_name)

    def _validate_entry(self, entry: TournamentEntry) -> None:
        """
        Validates that an entry can belong to this poule.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.

        Raises
        ------
        TypeError
            If `entry` is not a TournamentEntry object.
        ValueError
            If the entry belongs to another tournament.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be a TournamentEntry object - got {type(entry).__name__}')
        
        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry {entry.id} belongs to tournament {entry.tournament_id}, '
                             f'but poule {self.id} belongs to tournament {self.tournament_id}')

    def _validate_poule_size(self, size: int) -> None:
        """
        Validates that an official bout order exists for a poule size.

        Parameters
        ----------
        size : int
            The number of entries in the poule.

        Raises
        ------
        TypeError
            If `size` is not an integer.
        ValueError
            If `size` is not positive or has no supported bout order.
        """
        validation.validate_positive_int(size, 'size', 'Poule', '_validate_poule_size')
        supported_sizes = list(POULE_BOUT_ORDER.keys())
        supported_sizes.sort()
        
        if size not in supported_sizes:
            raise ValueError(f'Cannot create a poule with {size} entries because no official '
                             f'bout order exists for that size - supported sizes are {supported_sizes}')

    def _validate_entries(self, entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validates the tournament entries used to create this poule.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The tournament entries to validate.

        Raises
        ------
        TypeError
            If `entries` is not a tuple or contains an item that is not a
            TournamentEntry object.
        ValueError
            If fewer than two entries are provided, an entry is repeated or
            belongs to another tournament, or no bout order exists for the
            poule size.
        """
        # Validate that a tuple is provided
        if not isinstance(entries, tuple):
            raise TypeError(f'Entries must be a tuple - got {type(entries).__name__}')
        
        # Ensure enough entries are provided
        if len(entries) < 2:
            raise ValueError(f'There must be at least two entries in a poule - got {len(entries)}')
        
        # Validate each entry
        seen_entry_ids: set[int] = set()

        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Each entry must be a TournamentEntry object - entry at index {i} is a {type(entry).__name__}')
                
            if entry.tournament_id != self.tournament_id:
                raise ValueError(f'Entry {entry.id} at index {i} belongs to tournament {entry.tournament_id}, '
                                 f'but poule {self.id} belongs to tournament {self.tournament_id}')

            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry {entry.id} appears more than once - duplicate found at index {i}')

            seen_entry_ids.add(entry.id)

        # Validate that a bout order exists for this size
        self._validate_poule_size(len(entries))

    def _validate_match_pair(self, match_pair: tuple[int, int], entries: tuple[TournamentEntry, ...], method_name: str) -> None:
        """
        Validates a pair of fencer numbers from a poule bout order.

        Fencer numbers are one-based and refer to positions in `entries`.

        Parameters
        ----------
        match_pair : tuple[int, int]
            The two fencer numbers to validate.
        entries : tuple[TournamentEntry, ...]
            The validated poule entries in fencer-number order.
        method_name : str
            The name of the method requesting the validation.

        Raises
        ------
        TypeError
            If `method_name` is not a string, `match_pair` is not a tuple, or
            either fencer number is not an integer.
        ValueError
            If `match_pair` does not contain exactly two fencer numbers, a fencer
            number is outside the valid range, or both numbers are the same.
        """
        if not isinstance(method_name, str):
            raise TypeError(f'method_name must be a string in Poule._validate_match_pair() - got {type(method_name).__name__}')
        
        # Validate the match pair tuple
        if not isinstance(match_pair, tuple):
            raise TypeError(f'Match pair must be a tuple in Poule.{method_name}() - got {type(match_pair).__name__}')
        
        if len(match_pair) != 2:
            raise ValueError(f'Match pair must contain exactly two fencer numbers in '
                             f'Poule.{method_name}() - got {len(match_pair)}')
        
        # Validate the fencer numbers in the pair
        fencer_number1, fencer_number2 = match_pair

        validation.validate_int_in_range(fencer_number1, 1, len(entries), 'First fencer number', 'Poule', method_name)
        validation.validate_int_in_range(fencer_number2, 1, len(entries), 'Second fencer number', 'Poule', method_name)

        if fencer_number1 == fencer_number2:
            raise ValueError(f'A poule match must contain two different fencer numbers in Poule.{method_name}() - got {fencer_number1} twice')
