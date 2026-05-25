from dataclasses import dataclass, field
from tournament_entry import TournamentEntry
from functools import total_ordering

@dataclass
@total_ordering
class EntryPouleResult:
    entry: TournamentEntry
    poule_id: int
    matches_fenced: int = 0
    victories: int = 0
    touches_scored: int = 0
    touches_received: int = 0

    def __post_init__(self):
        # Validate types
        if not isinstance(self.entry, TournamentEntry):
            raise TypeError('Entry must be of type TournamentEntry')
        if type(self.poule_id) is not int:
            raise TypeError('Poule ID must be an integer')
        if type(self.matches_fenced) is not int:
            raise TypeError('Matches fenced must be an integer')
        if type(self.victories) is not int:
            raise TypeError('Victories must be an integer')
        if type(self.touches_scored) is not int:
            raise TypeError('Touches scored must be an integer')
        if type(self.touches_received) is not int:
            raise TypeError('Touches received must be an integer')
        
        # Validate values
        if self.poule_id < 1:
            raise ValueError('Poule ID must be a positive integer')
        if self.matches_fenced < 0:
            raise ValueError('Matches fenced must be a non-negative integer')
        if self.victories < 0:
            raise ValueError('Victories must be a non-negative integer')
        if self.touches_scored < 0:
            raise ValueError('Touches scored must be a non-negative integer')
        if self.touches_received < 0:
            raise ValueError('Touches received must be a non-negative integer')

    def __str__(self):
        return f'{self.entry.fencer.display_name}: V = {self.victories}, TS = {self.touches_scored}, TR = {self.touches_received}'
                
    def __eq__(self, other):
        try:
            self_ratio = self.victories / self.matches_fenced
        except ZeroDivisionError:
            self_ratio = 0
        try:
            other_ratio = other.victories / other.matches_fenced
        except ZeroDivisionError:
            other_ratio = 0

        self_indicator = self.touches_scored - self.touches_received
        other_indicator = other.touches_scored - other.touches_received
        
        return self_ratio == other_ratio and self_indicator == other_indicator and self.touches_scored == other.touches_scored
    
    def __gt__(self, other):
        # First, compare ratio
        try:
            self_ratio = self.victories / self.matches_fenced
        except ZeroDivisionError:
            self_ratio = 0
        try:
            other_ratio = other.victories / other.matches_fenced
        except ZeroDivisionError:
            other_ratio = 0

        if self_ratio > other_ratio:
            return True
        elif self_ratio < other_ratio:
            return False
        else:
            # Second, compare indicator
            self_indicator = self.touches_scored - self.touches_received
            other_indicator = other.touches_scored - other.touches_received
            if self_indicator > other_indicator:
                return True
            elif self_indicator < other_indicator:
                return False
            else:
                # Third, compare TS
                if self.touches_scored > other.touches_scored:
                    return True
                elif self.touches_scored < other.touches_scored:
                    return False
                else:
                    # All comparison metrics are equal (== case)
                    return False

    def add_match_result(self, touches_scored: int, touches_received: int, is_victory: bool) -> None:
        """Adds a match result to the stored results for this specific entry."""
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
        self.matches_fenced += 1
        if is_victory:
            self.victories += 1
        self.touches_scored += touches_scored
        self.touches_received += touches_received

    def __str__(self):
        return f'{self.entry.fencer.display_name}: M = {self.matches_fenced}, V = {self.victories}, TS = {self.touches_scored}, TR = {self.touches_received}, I = {self.touches_scored - self.touches_received}'

@dataclass
class PouleResult:
    poule_id: int
    results: list[EntryPouleResult] = field(default_factory=list) # List mirrors the order of the entries in the poule; this is not necessarily sorted by the results

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
        return [result.entry.display_name() for result in standings]

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
class PouleResults:
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
