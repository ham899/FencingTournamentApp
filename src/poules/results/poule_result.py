from collections.abc import Iterable
from dataclasses import dataclass, field, InitVar

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.results.poule_entry_result import PouleEntryResult


@dataclass(slots=True)
class _PouleEntryStats:
    """
    Stores mutable per-entry statistics while calculating a PouleResult.
    
    Attributes
    ----------
    num_matches : int, default=0
        The number of completed poule bouts fenced by the entry.
    num_victories : int, default=0
        The number of completed poule bouts won by the entry.
    touches_scored : int, default=0
        The total number of touches scored by the entry in completed poule bouts.
    touches_received : int, default=0
        The total number of touches scored against the entry in completed poule bouts.
    """
    num_matches: int = 0
    num_victories: int = 0
    touches_scored: int = 0
    touches_received: int = 0


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the provided attributes.
        
        Raises
        ------
        TypeError
            If num_matches, num_victories, touches_scored, or touches_received is not an integer.
        ValueError
            If num_matches, num_victories, touches_scored, or touches_received is negative, 
            if the number of victories is greater than the number of completed matches, or if 
            touches scored or touches received are present when no matches have been done.
        """
        validation.validate_non_negative_int(self.num_matches, 'Number of matches', '_PouleEntryStats')
        validation.validate_non_negative_int(self.num_victories, 'Number of victories', '_PouleEntryStats')
        validation.validate_non_negative_int(self.touches_scored, 'Touches scored', '_PouleEntryStats')
        validation.validate_non_negative_int(self.touches_received, 'Touches received', '_PouleEntryStats')

        if self.num_victories > self.num_matches:
            raise ValueError(f'The number of victories cannot exceed the number of matches in _PouleEntryStats - got {self.num_victories} victories and {self.num_matches} matches')
        
        if self.num_matches == 0:
            if self.touches_scored > 0:
                raise ValueError(f'Touches scored must be 0 when no matches have been completed in _PouleEntryStats - got {self.touches_scored}')
            if self.touches_received > 0:
                raise ValueError(f'Touches received must be 0 when no matches have been completed in _PouleEntryStats - got {self.touches_received}')


    # --- Properties ---
    @property
    def stats(self) -> tuple[int, int, int, int]:
        """Return statistics as matches, victories, touches scored, and touches received."""
        return self.num_matches, self.num_victories, self.touches_scored, self.touches_received


    # --- Counter Methods ---
    def add_match(self) -> None:
        """Adds one match count to the total count of matches."""
        self.num_matches += 1

    def add_victory(self) -> None:
        """Adds one victory count to the total count of victories."""
        self.num_victories += 1

    def add_touches_scored(self, touches: int) -> None:
        """
        Adds the specified number of touches to total touches scored count.
        
        Parameters
        ----------
        touches : int
            The number of touches to add.
        """
        self.touches_scored += touches

    def add_touches_received(self, touches: int) -> None:
        """
        Adds the specified number of touches to total touches received count.
        
        Parameters
        ----------
        touches : int
            The number of touches to add.
        """
        self.touches_received += touches


@dataclass(frozen=True, slots=True)
class PouleResult:
    """
    Represents a calculated snapshot of the current results in a poule.

    Results are derived from completed poule matches. Incomplete matches are
    ignored, and the matches remain the source of truth. Entry results preserve
    the order of the supplied entries.

    Parameters
    ----------
    poule_entries : Iterable[TournamentEntry]
        The entries whose results are calculated.
    poule_matches : Iterable[PouleMatch]
        The complete round-robin schedule from which results are derived.
    poule_id : int
        The unique identifier of the poule.
    tournament_id : int
        The unique identifier of the tournament containing the poule.

    Attributes
    ----------
    entry_results : tuple[PouleEntryResult, ...]
        The calculated result for each entry, in the order the entries were supplied.
    poule_id : int
        The unique identifier of the poule.
    tournament_id : int
        The unique identifier of the tournament containing the poule.
    """
    poule_entries: InitVar[Iterable[TournamentEntry]]
    poule_matches: InitVar[Iterable[PouleMatch]]

    entry_results: tuple[PouleEntryResult, ...] = field(init=False)
    poule_id: int
    tournament_id: int
    
    
    # --- Initialization and Validation Methods ---
    def __post_init__(self, poule_entries: Iterable[TournamentEntry], poule_matches: Iterable[PouleMatch]) -> None:
        """
        Validate the inputs and calculate the entry results.

        Parameters
        ----------
        poule_entries : Iterable[TournamentEntry]
            The entries belonging to the poule.
        poule_matches : Iterable[PouleMatch]
            The matches belonging to the poule.

        Raises
        ------
        TypeError
            If either ID is not an integer, if `poule_entries` or `poule_matches`
            is not iterable, or if either iterable contains an object of the
            wrong type.
        ValueError
            If either ID is not positive, fewer than two entries are provided,
            entry IDs are not unique, an entry belongs to another tournament,
            the required number of matches is not provided, a match belongs to
            another poule or tournament, a match contains an invalid entry, or
            match IDs, match indices, or entry pairings are not unique.
        RuntimeError
            If a completed match does not have a valid winner index.
        """
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleResult')
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleResult')
        
        if not isinstance(poule_entries, Iterable):
            raise TypeError(f'Provided entries in PouleResult must be an iterable - got {type(poule_entries).__name__}')
        
        if not isinstance(poule_matches, Iterable):
            raise TypeError(f'Provided poule matches in PouleResult must be an iterable - got {type(poule_matches).__name__}')
        
        # Convert entries and matches iterables into tuples
        entries = tuple(poule_entries)
        matches = tuple(poule_matches)

        self._validate_entries(entries)
        self._validate_matches(matches, entries)
                
        object.__setattr__(self, 'entry_results', self._calculate_results_from_matches(entries, matches))


    # --- Properties ---
    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """Returns the entries represented by this poule result."""
        return tuple(result.entry for result in self.entry_results)
    
    @property
    def ranked_results(self) -> tuple[PouleEntryResult, ...]:
        """Returns the tuple of poule entry results in descending ranked order."""
        return self._calculate_ranked_results()
    

    # --- Result Calculation Helper Methods ---
    def _calculate_results_from_matches(self, entries: tuple[TournamentEntry, ...], matches: tuple[PouleMatch, ...]) -> tuple[PouleEntryResult, ...]:
        """
        Calculate one result for each entry from the completed matches.

        Incomplete matches are ignored.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries whose results are calculated.
        matches : tuple[PouleMatch, ...]
            The matches from which results are derived.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The calculated results in the same order as `entries`.

        Raises
        ------
        RuntimeError
            If a completed match does not have a valid winner index.
        """
        # Create a dictionary of entry IDs and poule results initialized to zero to act as a counter variable
        results_tracker: dict[int, _PouleEntryStats] = {}

        for entry in entries:
            results_tracker[entry.id] = _PouleEntryStats()

        for match in matches:
            if match.is_complete():
                # Extract the winner index of the match
                winner_index = match.winner_index()

                if winner_index not in (0, 1):
                    raise RuntimeError(f'Completed poule match {match.id} has an invalid winner index of {winner_index} in PouleResult._calculate_results_from_matches().')

                # Add match result info to each entry's result stats
                for entry_index, entry in enumerate(match.entries):
                    entry_stats = results_tracker[entry.id]
                    
                    entry_stats.add_match()

                    if entry_index == winner_index:
                        entry_stats.add_victory()
                    
                    if entry_index == 0:
                        entry_stats.add_touches_scored(match.score1)
                        entry_stats.add_touches_received(match.score2)
                    else: 
                        entry_stats.add_touches_scored(match.score2)
                        entry_stats.add_touches_received(match.score1)

        # Create a list of the derived PouleEntryResult statistics
        entry_results: list[PouleEntryResult] = []
        for entry in entries:
            num_matches, num_victories, touches_scored, touches_received = results_tracker[entry.id].stats
            entry_results.append(PouleEntryResult(entry, self.poule_id, self.tournament_id, num_matches, num_victories, touches_scored, touches_received))

        return tuple(entry_results)
    
    def _calculate_ranked_results(self) -> tuple[PouleEntryResult, ...]:
        """
        Return the entry results in descending display order.

        Results are ordered by victory ratio, indicator, and touches scored.
        Exact ties are ordered alphabetically by display name. Alphabetical
        ordering is for display only and is not a seeding tiebreaker.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending display order.
        """
        # Copy the entry results to a mutable list
        entry_results_list = list(self.entry_results)

        # First sort by alphabetical order as that order will be used for poule result display over randomization
        entry_results_list.sort(key=lambda result: result.display_name)

        # Sort by result statistics second - alphabetical order is maintained as the sort method is stable
        entry_results_list.sort(key=lambda result: (result.victory_ratio, result.indicator, result.touches_scored), reverse=True)

        return tuple(entry_results_list)


    # --- Validation Helper Methods ---
    def _validate_entries(self, entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validates the given entries.

        Parameters
        ----------
        entries : tuple[TournamentEntry, ...]
            The entries to validate.

        Raises
        ------
        TypeError
            If entries is not a tuple, or if any entry in entries is not a `TournamentEntry` object.
        ValueError
            If fewer than two entries are provided, an entry belongs to another
            tournament, or entry IDs are not unique.
        """
        if not isinstance(entries, tuple):
            raise TypeError(f'Provided entries in PouleResult must be a tuple - got {type(entries).__name__}')
        
        if len(entries) < 2:
            raise ValueError(f'Provided entries in PouleResult must contain at least 2 items - got {len(entries)} items')

        seen_entry_ids: set[int] = set()

        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Entry at index {i} in entries in PouleResult must be a TournamentEntry object - got {type(entry).__name__}')
        
            if entry.tournament_id != self.tournament_id:
                raise ValueError(f'Entry at index {i} in entries in PouleResult has tournament ID {entry.tournament_id}, which does not equal this PouleResult container\'s tournament ID {self.tournament_id}')

            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry ID {entry.id} occurs more than once in entries - duplicate found at index {i}')
            
            seen_entry_ids.add(entry.id)

    def _validate_matches(self, matches: tuple[PouleMatch, ...], entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validates the provided poule matches.

        Parameters
        ----------
        matches : tuple[PouleMatch, ...]
            The poule matches to validate.
        entries : tuple[TournamentEntry, ...]
            The entries permitted to appear in the matches.

        Raises
        ------
        TypeError
            If matches is not a tuple, or if matches contains an item that is not a PouleMatch.
        ValueError
            If no matches are provided, the number of matches does not form a
            complete round-robin schedule, a match belongs to another poule or
            tournament, a match contains an invalid entry, or match IDs, match
            indices, or entry pairings are not unique.
        """
        if not isinstance(matches, tuple):
            raise TypeError(f'The provided matches must be in a tuple - got {type(matches).__name__}')
        
        if not matches:
            raise ValueError(f'There must be at least one match present - got {len(matches)} matches')

        expected_num_matches = len(entries) * (len(entries) - 1) // 2

        if len(matches) != expected_num_matches:
            raise ValueError(f'Expected {expected_num_matches} matches for {len(entries)} entries, but actually got {len(matches)} matches')
        
        valid_entry_ids: set[int] = {entry.id for entry in entries}
        seen_match_ids: set[int] = set()
        seen_match_indices: set[int] = set()
        seen_entry_id_pairs: set[frozenset[int]] = set()

        for i, match in enumerate(matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'Item at index {i} in matches must be a PouleMatch object - got {type(match).__name__}')
            
            if match.poule_id != self.poule_id:
                raise ValueError(f'The poule match at index {i} in matches does not have the same poule ID {match.poule_id} as the poule ID of this result container {self.poule_id}')

            if match.tournament_id != self.tournament_id:
                raise ValueError(f'The poule match at index {i} in matches does not have the same tournament ID {match.tournament_id} as the tournament ID this result container {self.tournament_id}')
                        
            if match.id in seen_match_ids:
                raise ValueError(f'Poule match {match.id} occurs more than once in matches')
            
            if match.match_index in seen_match_indices:
                raise ValueError(f'Match index {match.match_index} occurs more than once in matches')
            
            for entry in match.entries:
                if entry.id not in valid_entry_ids:
                    raise ValueError(f'Poule match {match.id} contains entry {entry.id}, which is not a valid entry ID in this poule result container')
            
            entry_id_pair = frozenset((match.entry1.id, match.entry2.id))

            if entry_id_pair in seen_entry_id_pairs:
                raise ValueError(f'Entries {match.entry1.id} and {match.entry2.id} occur together in more than one match')

            seen_match_ids.add(match.id)
            seen_match_indices.add(match.match_index)
            seen_entry_id_pairs.add(entry_id_pair)

        expected_match_indices = set(range(len(matches)))

        if seen_match_indices != expected_match_indices:
            raise ValueError(f'Match indices in PouleResult must be consecutive and start at 0 - got {seen_match_indices}')