from dataclasses import dataclass, field, InitVar
from typing import Self

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.results.poule_entry_result import PouleEntryResult


@dataclass
class PouleResult:
    """
    Represents all the entries' results in a poule.
    The list of poule entry results is ordered the same as the list of entries in the poule.
    This is not meant to store results, but rather to be a derived snapshot of the results in poule.
    However, ultimately, the poule matches themselves remain the source of truth for the results.

    
    Attributes
    ----------
    poule_entries : InitVar[list[TournamentEntry]]
        A list of TournamentEntry objects for which to hold results for.
    
    poule_id : int
        The unique identifier of the poule this results container belongs to.
    tournament_id : int
        The unique identifier of the tournament this poule belongs to.

    entry_results : list[PouleEntryResult], init=False
        A list of the poule entry results for each entry in the poule, meant to be ordered the same as the list of entries in the poule.
    """
    poule_entries: InitVar[list[TournamentEntry]]

    poule_id: int
    tournament_id: int

    entry_results: list[PouleEntryResult] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, poule_entries: list[TournamentEntry]) -> None:
        """
        Validates the PouleResult attributes and sets the entry_results attribute to a list of initialized poule entry result objects.
        
        Parameters
        ----------
        poule_entries : list[TournamentEntry]
            A list of TournamentEntry objects for which to hold results for.
        
        Raises
        ------
        TypeError
            If the poule ID is not an integer, or if the entries is not a list of TournamentEntry objects.
        ValueError
            If the poule ID is not a positive integer, or if the entries list contains less than 2 TournamentEntry objects.
        """
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'PouleResult')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'PouleResult')
        self._validate_entry_list(poule_entries)
                
        # Create list of initialized PouleEntryResults for each poule entry
        self.entry_results = [PouleEntryResult(entry, self.poule_id, self.tournament_id) for entry in poule_entries]


    # --- Alternative Constructors ---
    @classmethod
    def from_matches(cls, poule_entries: list[TournamentEntry], matches: list[PouleMatch], poule_id: int, tournament_id: int) -> Self:
        """
        Creates a PouleResult and calculates its entry results from the provided poule matches.

        Parameters
        ----------
        poule_entries : list[TournamentEntry]
            The entries represented by the result snapshot.
        matches : list[PouleMatch]
            The poule matches from which to calculate the results.
        poule_id : int
            The identifier of the poule.
        tournament_id : int
            The identifier of the tournament.

        Returns
        -------
        PouleResult
            A newly created result snapshot populated from the matches.

        Raises
        ------
        TypeError
            If the poule ID or tournament ID is not an integer, if poule_entries is not a list,
            if any element of poule_entries is not a TournamentEntry object, if matches is not a list,
            or if any element of matches is not a PouleMatch object.
        ValueError
            If the poule ID or tournament ID is not positive, if poule_entries contains fewer than
            two entries, if an entry appears more than once, if an entry belongs to a different
            tournament, if a match belongs to a different tournament or poule, if a match contains
            an entry not represented by this result snapshot, or if a match appears more than once.
        """
        poule_result = cls(poule_entries, poule_id, tournament_id)
        poule_result._compute_results_from_matches(matches)
        return poule_result


    # --- Properties ---
    @property
    def entries(self) -> list[TournamentEntry]:
        """Returns the entries represented by this poule result."""
        return [result.entry for result in self.entry_results]
    

    # --- Result Calculation Methods ---
    def calculate_standings(self) -> list[PouleEntryResult]:
        """Returns a list of the poule entry results ordered such that the "best" results are at the front of the list."""
        return sorted(self.entry_results, key=lambda result: (result.ratio, result.indicator, result.touches_scored), reverse=True)

    def calculate_standings_display_names(self) -> list[str]:
        """Returns the results as a list of display names in ranked order, where the highest ranked entry is at the front of the list."""
        return [result.display_name for result in self.calculate_standings()]


    # --- State Update Helper Methods ---
    def _reset(self) -> None:
        """Resets every poule entry result back to all zeroed result values"""
        for result in self.entry_results:
            result._reset()


    # --- Result Update Helper Methods ---
    def _add_match_result(self, match: PouleMatch) -> None:
        """
        Adds the result of a completed poule match to both participating entries in the match to their respective PouleEntryResult containers.
        
        Parameters
        ----------
        match : PouleMatch
            A **completed** poule match containing two entries whose results will be added to their respective PouleEntryResult containers.

        Raises
        ------
        TypeError
            If the input match is not a poule match.
        ValueError
            If the match does not have the same tournament ID or poule ID as the PouleResult container's tournament or poule ID, if an entry in the match
            does not exist in this PouleResult container, or if the match is not complete yet.
        """
        self._validate_match(match, '_add_match_result')

        if match.is_incomplete():
            raise ValueError(f'Cannot add the incomplete match {match.id} to PouleResult for poule {self.poule_id} in PouleResult._add_match_result()')
        
        for entry_result in self.entry_results:
            entry_result._add_match_result(match) # Note: The entry_result.add_match_result() method does not make an update if the entry is not in the match

    def _compute_results_from_matches(self, matches: list[PouleMatch]) -> None:
        """
        Recalculates all entry results from the provided poule matches.
        
        Parameters
        ----------
        matches : list[PouleMatch]
            The matches for which to populate the results with.

        Raises
        ------
        TypeError
            If the input matches is not a list, or if any of its elements is not a PouleMatch object.
        ValueError
            If any of its matches does not have the same tournament or poule ID as this result container, 
            or if any of the matches has an entry that does not exist in this result container.
        """
        self._validate_matches(matches, '_compute_results_from_matches')

        # Reset each poule entry's results back to zero
        self._reset()
        
        # Populate the zeroed results from the matches input
        for match in matches:
            if match.is_complete():
                self._add_match_result(match)


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry, method_name: str | None = None, *, index: int | None = None) -> None:
        """
        Validates if an entry is valid for a PouleResult container.
        
        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.
        method_name : str | None
            The name of the method that this validation method is being used in.
        index : int | None
            An optional index value for cases where the validation is being iterated through a list.

        Raises
        ------
        TypeError
            If the entry is not a TournamentEntry object, if method_name is not either None or a string, or if index is not either None or a int.
        ValueError
            If the tournament entry's tournament ID does not match the PouleResult container's tournament ID, or if the index is a negative integer.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name in PouleResult._validate_entry() must be either None or a string - got {type(method_name).__name__}')

        if index is not None:
            validation.validate_non_negative_int(index, 'index', 'PouleResult', '_validate_entry')

        method_suffix = '' if method_name is None else f'.{method_name}()'
        index_suffix = '' if index is None else f' at index {index}'

        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry{index_suffix} must be a TournamentEntry object in PouleResult{method_suffix} - got {type(entry).__name__}')
        
        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry{index_suffix} has tournament ID {entry.tournament_id} which does not equal this PouleResult container\'s tournament ID {self.tournament_id} in PouleResult{method_suffix}')

    def _validate_entry_list(self, entries: list[TournamentEntry], method_name: str | None = None) -> None:
        """
        Validates a given list of TournamentEntry objects.

        Parameters
        ----------
        entries : list[TournamentEntry]
            A list of TournamentEntry objects to validate.
        method_name : str | None
            The name of the method that this validation method is being used in.

        Raises
        ------
        TypeError
            If entries is not a list, if method_name is not either None or a string, or if any entry in entries is not a TournamentEntry object.
        ValueError
            If an entry in entries has a tournament ID that does not match the PouleResult container's tournament ID, 
            if an entry appears more than once in entries, or if there are fewer than two elements in entries.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name in PouleResult._validate_entry_list() must be either None or a string - got {type(method_name).__name__}')

        method_suffix = '' if method_name is None else f'.{method_name}()'

        if not isinstance(entries, list):
            raise TypeError(f'entries in PouleResult{method_suffix} must be in a list - got {type(entries).__name__}')

        for i, entry in enumerate(entries):
            self._validate_entry(entry, method_name, index=i)

            if entries.count(entry) != 1:
                raise ValueError(f'Entry at index {i} appears more than once in PouleResult{method_suffix}')
            
        if len(entries) < 2:
            raise ValueError(f'Provided entries must contain at least 2 TournamentEntry objects in PouleResult - got {len(entries)}')

    def _validate_match(self, match: PouleMatch, method_name: str | None = None, *, index: int | None = None) -> None:
        """
        Validates that the input match is a poule match that can belong to this poule result container.

        Parameters
        ----------
        match : PouleMatch
            A poule match to validate.
        method_name : str | None
            The name of the method that this validation method is being used in.
        index : int | None
            An optional index value for cases where the validation is being iterated through a list.

        Raises
        ------
        TypeError
            If match is not a PouleMatch object, if method_name is not either None or a string, or if index is not either None or an integer.
        ValueError
            If the match's tournament ID does not match the PouleResult container's tournament ID, 
            if the match's poule ID does not match the PouleResult container's poule ID,
            if either of the entries in the match are not in the PouleResult container, or if index is negative.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name in PouleResult._validate_match() must be either None or a string - got {type(method_name).__name__}')
        
        if index is not None:
            validation.validate_non_negative_int(index, 'index', 'PouleResult', '_validate_match')
        
        method_suffix = '' if method_name is None else f'.{method_name}()'
        index_suffix = '' if index is None else f' at index {index}'
    
        if not isinstance(match, PouleMatch):
            raise TypeError(f'Match{index_suffix} must be a PouleMatch object in PouleResult{method_suffix} - got {type(match)}')

        if match.tournament_id != self.tournament_id:
            raise ValueError(f'Match{index_suffix} has tournament ID {match.tournament_id} which does not match the container\'s tournament ID {self.tournament_id} in PouleResult{method_suffix}')
        
        if match.poule_id != self.poule_id:
            raise ValueError(f'Match{index_suffix} has poule ID {match.poule_id} which does not match the container\'s poule ID {self.poule_id} in PouleResult{method_suffix}')

        for entry in match.entries():
            if entry not in self.entries:
                raise ValueError(f'Match{index_suffix} contains an entry that is not in the poule {self.poule_id} in PouleResult{method_suffix}')

    def _validate_matches(self, matches: list[PouleMatch], method_name: str | None) -> None:
        """
        Validates a list of PouleMatch objects.
        
        Parameters
        ----------
        matches : list[PouleMatch]
            The list of poule matches to validate.

        Raises
        ------
        TypeError
            If matches is not a list, if any match in matches is not a PouleMatch, or if method_name is not either None or a string.
        ValueError
            If a match in matches has a tournament ID or poule ID that does not match the PouleResult container's tournament ID or poule ID, 
            or if a match has an entry that is not in the PouleResult container, or if a match appears more than once in the list.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name in PouleResult._validate_matches() must be either None or a string')
        
        method_suffix = '' if method_name is None else f'.{method_name}()'

        if not isinstance(matches, list):
            raise TypeError(f'The input list of matches in PouleResult{method_suffix} must be a list - got {type(matches).__name__}')
        
        for i, match in enumerate(matches):
            self._validate_match(match, method_name, index=i)

            if matches.count(match) != 1:
                raise ValueError(f'Match at index {i} appears more than once in PouleResult{method_suffix}')