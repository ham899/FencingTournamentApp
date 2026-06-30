from dataclasses import dataclass, field, InitVar
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


    # --- Initialization and Validation Methods ---
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


    # --- Properties ---
    @property
    def display_name(self) -> str:
        """Returns the display name of the entry."""
        return self.entry.display_name


    # --- Dunder Methods ---                
    def __eq__(self, other):
        """Compares the equality of a EntryPouleResult and another object."""
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


    # --- Result Update Methods ---
    def add_match_result(self, match: PouleMatch) -> None:
        """
        Gets a **completed** poule match and adds the result to the EntryPouleResult container.

        **Note:** If the entry is not in the match, the EntryPouleResult container will not be updated.
        
        Parameters
        ----------
        match : PouleMatch
            A **completed** poule match containing this entry whose results will be added to the entry's results container.

        Raises
        ------
        TypeError
            If the match is not a PouleMatch object.
        ValueError
            If the match is incomplete.
        """
        if not isinstance(match, PouleMatch):
            raise TypeError(f'Match must be a PouleMatch object in EntryPouleResult.add_match_result() - got {type(match)}')

        if match.is_incomplete():
            raise ValueError(f'Cannot add the incomplete match {match.id} to entry {self.entry.id}\'s poule results container.')
        
        # If this entry is not in the match, don't update the entry's results
        if self.entry not in match.entries():
            return
        
        # Identify whether this entry is entry 1 or 2
        entry_index = 0 if match.entry1 == self.entry else 1

        # Extract the winner index of the match
        winner_index = match.winner_index()
        
        if winner_index is None:
            raise RuntimeError(f'The completed poule match {match.id} has no winner, which is an impossible state in EntryPouleResult.add_match_result().')

        # Add match result information
        self.matches += 1
        if entry_index == winner_index:
            self.victories += 1
        self.touches_scored += match.score1 if entry_index == 0 else match.score2
        self.touches_received += match.score2 if entry_index == 0 else match.score1



@dataclass
class SinglePouleResults:
    """
    Holds all the entry's results in a poule. The list of results mirrors the entries in the poule; it is **not** sorted by results.
    
    Attributes
    ----------
    poule_id : int
        The unique identifier of the poule this results container belongs to.
    
    results : list[EntryPouleResult], default=None, init=False
        A list of the entry poule results for each entry in the poule. Invariant: the order of the results in the list mirrors the order of the entries in the poule.

    entries : list[TournamentEntry]
        A list of TournamentEntry objects for which to hold results for. This is an InitVar and is not stored as an attribute in the SinglePouleResults object.

    """
    poule_id: int
    results: list[EntryPouleResult] = field(default=None, init=False)

    entries: InitVar[list[TournamentEntry]]


    # --- Initialization and Validation Methods ---
    def __post_init__(self, entries: list[TournamentEntry]) -> None:
        """
        Validates the SinglePouleResults attributes.
        
        Parameters
        ----------
        entries : list[TournamentEntry]
            A list of TournamentEntry objects for which to hold results for.
        
        Raises
        ------
        TypeError
            If the poule ID is not an integer, or if the entries is not a list of TournamentEntry objects.
        ValueError
            If the poule ID is not a positive integer, or if the entries list contains less than 2 TournamentEntry objects.
        """
        # Validate provided attributes
        validation.validate_positive_int(self.poule_id, 'Poule ID', 'SinglePouleResults')
        
        if not isinstance(entries, list):
            raise TypeError(f'Provided entries must be a list of TournamentEntry objects in SinglePouleResults - got {type(entries)}')
        
        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'All entries in entries must be TournamentEntry objects in SinglePouleResults - got {type(entry)} at index {i}')

        if len(entries) < 2:
            raise ValueError(f'Provided entries must contain at least 2 TournamentEntry objects in SinglePouleResults - got {len(entries)}')
        
        # Create list of EntryPouleResults initialized to 0 to hold in `results` attribute.
        self.results = []
        for entry in entries:
            self.results.append(EntryPouleResult(entry=entry, poule_id=self.poule_id))


    # --- Dunder Methods ---
    def __eq__(self, other):
        """Compares the equality of a SinglePouleResults and another object."""
        if not isinstance(other, SinglePouleResults):
            return False
        
        return self.poule_id == other.poule_id
 

    # --- Result Update Methods ---
    def add_match_result(self, match: PouleMatch) -> None:
        """
        Adds the result of a completed poule match to both participating entries in the match to their respective EntryPouleResult containers.
        
        Parameters
        ----------
        match : PouleMatch
            A **completed** poule match containing two entries whose results will be added to their respective EntryPouleResult containers.
        """
        if match.is_incomplete():
            raise ValueError(f'Cannot add the incomplete match {match.id} to the SinglePouleResults container for poule {self.poule_id} in SinglePouleResults.add_match_result().')
        
        for entry_result in self.results:
            entry_result.add_match_result(match) # If the entry is not in the match, the add_match_result method will not update the entry's results


    # --- Result Calculation Methods ---
    def calculate_standings(self) -> list[EntryPouleResult]:
        """Returns a list of the entry poule results sorted first by proportion of victories, then indicator, then touches scored; the greatest results are at the front of the list."""
        # Mutate a copy of the original results
        results_copy = list(self.results)

        if len(results_copy) == 0:
            return results_copy
        
        return self._quicksort(results_copy, low=0, high=len(results_copy)-1)
    

    def calculate_standings_display_names(self) -> list[str]:
        """Returns the results as a list of display names in ranked order; the highest ranked entry is at the front of the list."""
        return [result.display_name for result in self.calculate_standings()]


    # --- Helper Methods ---
    @staticmethod
    def _swap(results: list[EntryPouleResult], i: int, j: int) -> None:
        """
        Swaps two results in the input list of poule results in-place; the input list is modified in-place.
        
        Parameters
        ----------
        results : list[EntryPouleResult]
            The list of poule results to swap two elements in.
        i : int
            The index of the first result to swap.
        j : int
            The index of the second result to swap.
        """
        tmp = results[i]
        results[i] = results[j]
        results[j] = tmp


    @staticmethod
    def _partition(results: list[EntryPouleResult], low: int, high: int) -> int:
        """
        The partition function in the quicksort algorithm and returns the location of the pivot; the input list is modified in-place.
        
        Parameters
        ----------
        results : list[EntryPouleResult]
            The list of poule results to partition.
        low : int
            The index of the first element in the range to partition.
        high : int
            The index of the last element in the range to partition.
        """
        # Choose right most element as the pivot
        pivot = results[high]

        # Place results that are better than the pivot to the left and worse or equal results to the right
        i = low - 1
        for j in range(low, high):
            if results[j] > pivot:
                i += 1
                SinglePouleResults._swap(results, i, j)

        # Place pivot back into the correct position
        SinglePouleResults._swap(results, i+1, high)
        
        # Return the position of the pivot
        return i + 1
    

    @staticmethod
    def _quicksort(results: list[EntryPouleResult], low: int, high: int) -> list[EntryPouleResult]:
        """
        Applies a quicksort algorithm such that the entry results are sorted first by proportion of 
        victories, then indicator, then touches scored; the input list is modified in-place and returned.
        
        Parameters
        ----------
        results : list[EntryPouleResult]
            The list of poule results to sort.
        low : int
            The index of the first element in the range to sort.
        high : int
            The index of the last element in the range to sort.

        Returns
        -------
        list[EntryPouleResult]
            The sorted list of poule results.
        """
        if low < high:
            # Partition and get pivot index
            p = SinglePouleResults._partition(results, low, high)

            # Recursively sort remaining entries in list
            SinglePouleResults._quicksort(results, low, p-1)
            SinglePouleResults._quicksort(results, p+1, high)

        return results



@dataclass
class TournamentPouleResults:
    """
    Data container that holds the combined poule results. The key invarianet is that the list of results must remain in sorted order.
    
    Attributes
    ----------

    """
    tournament_id: int
    poule_results: list[SinglePouleResults]


    # --- Initialization and Validation Methods ---
    def __post_init__(self):
        """
        Validates the TournamentPouleResults attributes.

        Raises
        ------
        TypeError
            If the tournament ID is not an integer, or if the poule results is not a list of SinglePouleResults objects.
        ValueError
            If the tournament ID is not a positive integer.
        """
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'TournamentPouleResults')

        if not isinstance(self.poule_results, list):
            raise TypeError(f'Poule results must be a list of SinglePouleResults objects in TournamentPouleResults - got {type(self.poule_results)}')
        
        for i, poule_result in enumerate(self.poule_results):
            if not isinstance(poule_result, SinglePouleResults):
                raise TypeError(f'All poule results in poule results list must be SinglePouleResults objects in TournamentPouleResults - got {type(poule_result)} at index {i}')


    # --- Update Methods ---
    def add_poule_results(self, poule_result: SinglePouleResults) -> None:
        """
        Adds a new poule result to the tournament poule results container or overwrites an existing poule result if it already exists 
        in the tournament poule results container as the newer poule result is assumed to be more up-to-date than the existing one.
        
        Parameters
        ----------
        poule_result : SinglePouleResults
            A new poule result to add to the tournament poule results container.

        Raises
        ------
        TypeError
            If the poule result is not a SinglePouleResults object.
        """
        if not isinstance(poule_result, SinglePouleResults):
            raise TypeError(f'Poule result must be a SinglePouleResults object in TournamentPouleResults.add_poule_results() - got {type(poule_result)}')
        
        # Check if the poule result already exists in the tournament poule results container
        if poule_result in self.poule_results:
            index_location = self.poule_results.index(poule_result)

            # Overwrite the existing poule result with the new one - assume that the new one is more up-to-date
            self.poule_results[index_location] = poule_result
        
        # Otherwise, add the new poule result to the tournament poule results container
        else:
            self.poule_results.append(poule_result)


    # --- Result Calculation Methods ---
    def calculate_overall_standings(self) -> list[EntryPouleResult]:
        """Returns a list of the entry poule results sorted first by proportion of victories, then indicator, then touches scored; the greatest results are at the front of the list."""
        # Create a list of all entry poule results across all poules
        all_results = []
        for poule_result in self.poule_results:
            all_results.extend(poule_result.results)

        # If there are no results, return an empty list
        if len(all_results) == 0:
            return all_results
        
        # Sort the list of all results using the quicksort algorithm
        return SinglePouleResults._quicksort(all_results, low=0, high=len(all_results)-1)