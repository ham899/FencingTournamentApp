from dataclasses import dataclass, field
from functools import total_ordering

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch


@dataclass
@total_ordering
class EntryPouleResult:
    """
    A data container to hold a single entry's poule result based on the matches they've done in the poule. 
    
    **Note:** no matches done assumes a ratio of 0.0.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry for whose results are stored.
    poule_id : int
        The unique identifier of the poule this entry belongs to.
    matches : int
        The number of matches this entry has fenced in the poule.
    victories : int
        The number of victories this entry has gotten in the poule.
    touches_scored : int
        The number of touches scored in the poule.
    touches_received : int
        The number of touches opponents have scored on this fencer in the poule.
    """
    entry: TournamentEntry
    poule_id: int
    matches: int = 0
    victories: int = 0
    touches_scored: int = 0
    touches_received: int = 0

    # Initialization and Validation Methods
    def __post_init__(self):
        """
        Validates the EntryPouleResult attributes.

        Raises
        ------
        TypeError
            If the entry is not a TournamentEntry, if the poule ID, matches, victories, touches_scores, or touches_recieved is not an integer.
        ValueError
            If the poule ID is not a positive integer, or if matches, victories, touches_scored, or touches_received are negative.
        """
        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry in EntryPouleResult - got {type(self.entry)}')
        
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'EntryPouleResult')
        validation.validate_non_negative_int(self.matches, 'matches', 'EntryPouleResult')
        validation.validate_non_negative_int(self.victories, 'victories', 'EntryPouleResult')
        validation.validate_non_negative_int(self.touches_scored, 'touches_scored', 'EntryPouleResult')
        validation.validate_non_negative_int(self.touches_received, 'touches_received', 'EntryPouleResult')

    # --- Dunder Methods ---                
    def __eq__(self, other):
        """Compares the equality of two EntryPouleResult objects."""
        if not isinstance(other, EntryPouleResult):
            return False

        try:
            self_ratio = self.victories / self.matches
        except ZeroDivisionError:
            self_ratio = 0.0
        try:
            other_ratio = other.victories / other.matches
        except ZeroDivisionError:
            other_ratio = 0.0

        self_indicator = self.touches_scored - self.touches_received
        other_indicator = other.touches_scored - other.touches_received
        
        return self_ratio == other_ratio and self_indicator == other_indicator and self.touches_scored == other.touches_scored
    
    def __gt__(self, other):
        """Compares whether this EntryPouleResult object is greater than another EntryPouleResult object."""
        if not isinstance(other, EntryPouleResult):
            raise ValueError(f'Cannot perform an inequality comparison between an EntryPouleResult and {type(other)}')

        ## First, compare the ratios
        # Set ratio to 0.0 if an entry has fenced no matches
        try:
            self_ratio = self.victories / self.matches
        except ZeroDivisionError:
            self_ratio = 0.0
        try:
            other_ratio = other.victories / other.matches
        except ZeroDivisionError:
            other_ratio = 0.0

        # Compare ratios
        if self_ratio > other_ratio:
            return True
        elif self_ratio < other_ratio:
            return False
        
        ## Second, compare the indicators
        else:
            self_indicator = self.touches_scored - self.touches_received
            other_indicator = other.touches_scored - other.touches_received
            
            if self_indicator > other_indicator:
                return True
            
            elif self_indicator < other_indicator:
                return False
            
            ## Lastly, compare touches scored
            else:
                if self.touches_scored > other.touches_scored:
                    return True
                
                elif self.touches_scored < other.touches_scored:
                    return False
                
                ## If ratio, indicator, and touches scored are all equal, we have two equal EntryPouleResults - neither is "greater than"
                else:
                    return False

    def add_match_result(self, touches_scored: int, touches_received: int, is_victory: bool) -> None:
        """
        Adds a match result to the stored results for this specific entry.

        Parameters
        ----------
        
        """
        # Validate types
        if not type(touches_scored) is int:
            raise TypeError('Touches scored must be an integer')
        if not type(touches_received) is int:
            raise TypeError('Touches received must be an integer')
        if not isinstance(is_victory, bool):
            raise TypeError('Victory indicator must be a boolean')

        # Validate values
        if touches_scored < 0:
            raise ValueError('Touches scored must be a non-negative integer')
        if touches_received < 0:
            raise ValueError('Touches received must be a non-negative integer')
        if is_victory and touches_scored <= touches_received:
            raise ValueError('The entry cannot have a win if touches scored is less than or equal to touches received')
        if not is_victory and touches_scored >= touches_received:
            raise ValueError('The entry cannot have a loss if touches scored is greater than or equal to touches received')

        # Update stored results
        self.matches += 1
        if is_victory:
            self.victories += 1
        self.touches_scored += touches_scored
        self.touches_received += touches_received

    def add_match_result(self, match: PouleMatch) -> None:
        """
        Gets a **completed** poule match and adds the result to the EntryPouleResult container.
        
        Parameters
        ----------
        match : PouleMatch
            A **completed** poule match to add to the result container.
        """
        if match.is_incomplete():
            return # OR raise value ValueError




@dataclass
class SinglePouleResults:
    """ Holds all the entry's results in a poule. The list of results mirrors the entries in the poule; it is not sorted by results. """
    poule_id: int
    results: list[EntryPouleResult] = field(default_factory=list)

    def __post_init__(self):
        # Validate types
        if type(self.poule_id) is not int:
            raise TypeError('Poule ID must be an integer')
        if not isinstance(self.results, list):
            raise TypeError('Results must be a list object')
        if len(self.results) > 0:
            for r in self.results:
                if not isinstance(r, EntryPouleResult):
                    raise TypeError('Results must be a list of EntryPouleResult objects')
        
        # Validate values
        if self.poule_id < 1:
            raise ValueError('Poule ID must be a positive integer')
    
    def init_entry_poule_results(self, entries: list[TournamentEntry]) -> None:
        """Initializes the poule results with the given list of entries. The order of the entries in the list will be mirrored in the order of the results."""
        # Validate types
        if not isinstance(entries, list):
            raise TypeError('Entries must be a list of TournamentEntry objects')
        for e in entries:
            if not isinstance(e, TournamentEntry):
                raise TypeError('Entries must be a list of TournamentEntry objects')

        # Initialize results with default values for each entry
        self.results = []
        for e in entries:
            self.results.append(EntryPouleResult(entry=e, poule_id=self.poule_id))

    def add_match_result_to_entry(self, entry_index: int, touches_scored: int, touches_received: int, is_victory: bool) -> None:
        """Applies add_match_result method to the specified entry in the poule results."""
        # Validate types
        if type(entry_index) is not int:
            raise TypeError('Entry index must be an integer')
        if not type(touches_scored) is int:
            raise TypeError('Touches scored must be an integer')
        if not type(touches_received) is int:
            raise TypeError('Touches received must be an integer')
        if not isinstance(is_victory, bool):
            raise TypeError('Victory indicator must be a boolean')

        # Validate values
        if entry_index < 0 or entry_index >= len(self.results):
            raise ValueError('Entry index is out of bounds for the poule results')
        if touches_scored < 0:
            raise ValueError('Touches scored must be a non-negative integer')
        if touches_received < 0:
            raise ValueError('Touches received must be a non-negative integer')
        if is_victory and touches_scored <= touches_received:
            raise ValueError('The entry cannot have a win if touches scored is less than or equal to touches received')
        if not is_victory and touches_scored >= touches_received:
            raise ValueError('The entry cannot have a loss if touches scored is greater than or equal to touches received')

        self.results[entry_index].add_match_result(touches_scored, touches_received, is_victory)

    def calculate_standings(self) -> list[EntryPouleResult]:
        """Returns a list of the entry poule results sorted first by proportion of victories, then indicator, then touches scored."""
        # Mutate a copy of the original results
        results_copy = list(self.results)
        if len(results_copy) == 0:
            return results_copy
        return self._quicksort(results=results_copy, low=0, high=len(results_copy)-1)
    
    def calculate_standings_display_names(self) -> list[str]:
        """Returns the results as a list of display names in ranked order."""
        standings = self.calculate_standings()
        return [result.entry.display_name for result in standings]

    def _swap(self, results: list[EntryPouleResult], i: int, j: int) -> None:
        """Swaps two results in the input list of poule results in-place."""
        tmp = results[i]
        results[i] = results[j]
        results[j] = tmp

    def _partition(self, results: list[EntryPouleResult], low: int, high: int) -> int:
        """The partition function in the quicksort algorithm and returns the location of the pivot. The input list is modified in-place."""
        # Choose right most element as the pivot
        pivot = results[high]

        # Place results that are better than the pivot to the left and worse or equal results to the right
        i = low - 1
        for j in range(low, high):
            if results[j] > pivot:
                i += 1
                self._swap(results, i, j)

        # Place pivot back into the correct position
        self._swap(results, i+1, high)
        
        # Return the position of the pivot
        return i + 1

    def _quicksort(self, results: list[EntryPouleResult], low: int, high: int) -> list[EntryPouleResult]:
        """Applies a quicksort algorithm such that the entry results are sorted first by proportion of victories, 
        then indicator, then touches scored. The input list is modified in-place."""
        if low < high:
            # Partition and get pivot index
            p = self._partition(results, low, high)

            # Recursively sort remaining entries in list
            self._quicksort(results, low, p-1)
            self._quicksort(results, p+1, high)

        return results

    def __str__(self):
        ret = ''
        for result in self.results:
            ret += result.__str__() + '\n'
        return ret

@dataclass
class TournamentPouleResults:
    """Data container that holds the combined poule results. The key invarianet is that the list of results must remain in sorted order."""
    results: list[EntryPouleResult] = field(default_factory=list) # Invariant: must be a sorted list for the results to hold

    def __post_init__(self):
        # Validate types
        if not isinstance(self.results, list):
            raise TypeError('Results must be a list of EntryPouleResult objects')
        for r in self.results:
            if not isinstance(r, EntryPouleResult):
                raise TypeError('Results must be a list of EntryPouleResult objects')

        # Sort the inputed entry results upon initialization; this class must maintain this invariant
        self._quicksort(0, len(self.results)-1)

    def _swap(self, i: int, j: int) -> None:
        """Swaps two results in the list of tournament entries."""
        tmp = self.results[i]
        self.results[i] = self.results[j]
        self.results[j] = tmp

    def _partition(self, low: int, high: int) -> int:
        """The partition function in the quicksort algorithm and returns the location of the pivot."""
        # Choose right most element as the pivot
        pivot = self.results[high]

        # Place results that are better than the pivot to the left and worse or equal results to the right
        i = low - 1
        for j in range(low, high):
            if self.results[j] > pivot:
                i += 1
                self._swap(i,j)

        # Place pivot back into the correct position
        self._swap(i+1, high)
        
        # Return the position of the pivot
        return i + 1

    def _quicksort(self, low: int, high: int) -> None:
        """Applies a quicksort algorithm such that the entry results are sorted first by proportion of victories, 
        then indicator, then touches scored."""
        if low < high:
            # Partition and get pivot index
            p = self._partition(low, high)

            # Recursively sort remaining entries in list
            self._quicksort(low, p-1)
            self._quicksort(p+1, high)

    def __str__(self):
        ret = ''
        for result in self.results:
            ret += result.__str__() + '\n'
        return ret