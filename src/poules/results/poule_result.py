from dataclasses import dataclass, field, InitVar

import validation

from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.results.poule_entry_result import PouleEntryResult


@dataclass(slots=True)
class _PouleEntryStats:
    """
    Accumulates one entry's statistics while calculating a PouleResult.

    A new accumulator starts with all statistics at zero. Each call to `add_match_info()` 
    records one completed poule bout and updates all four statistics together.

    Attributes
    ----------
    num_matches : int
        The number of completed poule bouts accumulated. 
        Initialized to 0.
    num_victories : int
        The number of completed poule victories accumulated. 
        Initialized to 0.
    touches_scored : int
        The total number of touches scored in the accumulated bouts.
        Initialized to 0.
    touches_received : int
        The total number of touches received in the accumulated bouts.
        Initialized to 0.
    """
    num_matches: int = field(default=0, init=False)
    num_victories: int = field(default=0, init=False)
    touches_scored: int = field(default=0, init=False)
    touches_received: int = field(default=0, init=False)


    # --- Properties ---
    @property
    def stats(self) -> tuple[int, int, int, int]:
        """
        Return the accumulated statistics as a tuple.

        Returns
        -------
        tuple[int, int, int, int]
            The number of matches, number of victories, 
            touches scored, and touches received, in that order.
        """
        return (self.num_matches, self.num_victories, self.touches_scored, self.touches_received)


    # --- Stat Update Methods ---
    def add_match_info(self, is_victory: bool, touches_scored: int, touches_received: int) -> None:
        """
        Add one completed poule bout to the accumulated statistics.

        Parameters
        ----------
        is_victory : bool
            Whether the entry won the bout.
        touches_scored : int
            The number of touches scored by the entry in the bout.
        touches_received : int
            The number of touches scored against the entry in the bout.

        Raises
        ------
        TypeError
            If `is_victory` is not a bool, or if either touch total is not an integer.
        ValueError
            If either touch total is negative, if the scores are tied, or if
            `is_victory` is inconsistent with the scores.
        """
        if type(is_victory) is not bool:
            raise TypeError(f'is_victory in _PouleEntryStats.add_match_info() must be a bool - got {type(is_victory).__name__}')

        validation.validate_non_negative_int(touches_scored, 'touches scored', '_PouleEntryStats', 'add_match_info')
        validation.validate_non_negative_int(touches_received, 'touches received', '_PouleEntryStats', 'add_match_info')
        
        if touches_scored == touches_received:
            raise ValueError(f'Touches scored cannot equal touches received in _PouleEntryStats.add_match_info() - matches cannot end in ties')
        
        if is_victory and touches_scored < touches_received:
            raise ValueError(f'If is_victory is True, touches scored cannot be less than touches received in _PouleEntryStats.add_match_info()')

        if not is_victory and touches_scored > touches_received:
            raise ValueError(f'If is_victory is False, touches scored cannot be greater than touches received in _PouleEntryStats.add_match_info()')

        self.num_matches += 1
        self.num_victories += 1 if is_victory else 0
        self.touches_scored += touches_scored
        self.touches_received += touches_received


@dataclass(frozen=True, slots=True)
class PouleResult:
    """
    Represents a calculated snapshot of the current results in a poule.

    Results are derived from completed poule matches. Incomplete matches are
    ignored, and the matches remain the source of truth. Entry results preserve
    the order of the supplied entries.

    Parameters
    ----------
    poule_entries : tuple[TournamentEntry, ...]
        The entries whose results are calculated.
    poule_matches : tuple[PouleMatch, ...]
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
    poule_entries: InitVar[tuple[TournamentEntry, ...]]
    poule_matches: InitVar[tuple[PouleMatch, ...]]

    entry_results: tuple[PouleEntryResult, ...] = field(init=False)
    poule_id: int
    tournament_id: int
    
    
    # --- Initialization and Validation Methods ---
    def __post_init__(self, poule_entries: tuple[TournamentEntry, ...], poule_matches: tuple[PouleMatch, ...]) -> None:
        """
        Validate the inputs and calculate the entry results.

        Parameters
        ----------
        poule_entries : tuple[TournamentEntry, ...]
            The entries belonging to the poule.
        poule_matches : tuple[PouleMatch, ...]
            The matches belonging to the poule.

        Raises
        ------
        TypeError
            If either ID is not an integer, if `poule_entries` or `poule_matches`
            is not a tuple, or if either tuple contains an object of the wrong type.
        ValueError
            If either ID is not positive, fewer than two entries are provided,
            entry IDs are not unique, an entry belongs to another tournament,
            the required number of matches is not provided, a match belongs to
            another poule or tournament, a match contains the same entry twice, 
            a match contains an invalid entry, or match IDs, match indices, 
            or entry pairings are not unique.
        RuntimeError
            If a completed match does not have a valid winner index.
        """
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleResult')
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleResult')

        self._validate_entries(poule_entries)
        self._validate_matches(poule_matches, poule_entries)
                
        object.__setattr__(self, 'entry_results', self._calculate_results_from_matches(poule_entries, poule_matches))


    # --- Properties ---
    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """
        Return the entries represented by this poule result.

        Returns
        -------
        tuple[TournamentEntry, ...]
            The entries in the same order as `entry_results`.
        """        
        return tuple(result.entry for result in self.entry_results)
    
    @property
    def ranked_results(self) -> tuple[PouleEntryResult, ...]:
        """
        Return the entry results in descending poule ranking order.

        Results are ordered by victory ratio, indicator, and touches scored.
        Exact ties are ordered alphabetically by display name for consistent
        display; alphabetical order is not a seeding tiebreaker.

        Returns
        -------
        tuple[PouleEntryResult, ...]
            The entry results in descending poule ranking order.
        """
        return self._calculate_ranked_results()
    
    @property
    def ranked_results_display_names(self) -> tuple[str, ...]:
        """
        Return the display names in the same order as `ranked_results`.

        Returns
        -------
        tuple[str, ...]
            The entries' display names in descending poule ranking order.
        """        
        ranked_results = self.ranked_results
        return tuple(result.display_name for result in ranked_results)
    

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
                    
                    entry_stats.add_match_info(
                        is_victory = entry_index == winner_index, 
                        touches_scored = match.score1 if entry_index == 0 else match.score2, 
                        touches_received = match.score2 if entry_index == 0 else match.score1
                    )

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
            tournament, a match contains the same entry twice, a match contains an invalid entry, 
            or match IDs, match indices, or entry pairings are not unique.
        """
        if not isinstance(matches, tuple):
            raise TypeError(f'The provided matches must be a tuple - got {type(matches).__name__}')
        
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
                raise ValueError(f'The poule match at index {i} in matches does not have the same tournament ID {match.tournament_id} as the tournament ID of this result container {self.tournament_id}')
                        
            if match.id in seen_match_ids:
                raise ValueError(f'Poule match {match.id} occurs more than once in matches')
            
            if match.match_index in seen_match_indices:
                raise ValueError(f'Match index {match.match_index} occurs more than once in matches')
            
            if match.entry1 == match.entry2:
                raise ValueError(f'Poule match {match.id} cannot contain the same entry twice')

            for entry in match.entries:
                if entry.id not in valid_entry_ids:
                    raise ValueError(f'Poule match {match.id} contains entry {entry.id}, which is not a valid entry ID in this poule result container')
                
                if entry not in entries:
                    raise ValueError(f'Poule match {match.id} contains entry {entry.id}, which does not belong in this poule result container')
            
            entry_id_pair = frozenset((match.entry1.id, match.entry2.id))

            if entry_id_pair in seen_entry_id_pairs:
                raise ValueError(f'Entries {match.entry1.id} and {match.entry2.id} occur together in more than one match')

            seen_match_ids.add(match.id)
            seen_match_indices.add(match.match_index)
            seen_entry_id_pairs.add(entry_id_pair)

        expected_match_indices = set(range(len(matches)))

        if seen_match_indices != expected_match_indices:
            raise ValueError(f'Match indices in PouleResult must be consecutive and start at 0 - got {seen_match_indices}')