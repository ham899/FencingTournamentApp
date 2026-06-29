from dataclasses import dataclass, field

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule_results import EntryPouleResult, SinglePouleResults
from poules.poule_orders import POULE_BOUT_ORDER


@dataclass
class Poule:
    """
    Represents a single poule in a tournament. A poule contains entries and a list of poule matches such that all the entries fence each other in the poule.
    
    id : int
        The unique identifier of the poule.
    tournament_id : int
        The unique identifier of the tournament that the poule belongs to.
    poule_number : int
        The poule number itself - possible different from the ID depending on the implementation.
    entries : list[TournamentEntry]
        The tournament entries that belong to the poule. Must be ordered such that entry at index i is fencer i+1 in the poule.
    size : int, init=False
        The number of tournament entries in the poule.
    matches : list[PouleMatch], default=None, init=False
        The matches and the order that they are to be done in for the poule. 
        **Invariant:** they must always reflect the current list of entries in the poule.
    current_match_index : int, default=0, init=False
        The index of the current match to be done in the list of matches, as the matches are supposed to be done in order.
    """
    id: int
    tournament_id: int
    poule_number: int
    entries: list[TournamentEntry]
    matches: list[PouleMatch] = field(default=None, init=False) # Invariant: matches should reflect the current entries in the poule
    current_match_index: int = field(default=0, init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self):
        """ """
        # Validate attributes
        validation.validate_positive_int(self.id, 'ID', 'Poule')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'Poule')
        validation.validate_positive_int(self.poule_number, 'Poule number', 'Poule')
        self._validate_own_entries_list()

        self.entries = list(self.entries) # Make a copy of the entries list

        # Generate the matches
        self._generate_own_matches()


    # --- Properties ---
    @property
    def size(self):
        """The size of the poule; the number of entries in the poule."""
        return len(self.entries)

    @property
    def number_matches(self) -> int:
        """The number of matches that need to occur to complete the poule."""
        return self.size * (self.size - 1) // 2


    # --- Dunder Methods ---
    def __eq__(self, other: object):
        """Evaluates the equality between a Poule and another object."""
        if not isinstance(other, Poule):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id


    # --- Predicate Methods ---
    def is_complete(self) -> bool:
        """Checks if the poule is complete."""
        if self.matches is None:
            return False
        return all(match.is_complete() for match in self.matches)


    # --- Access Methods ---
    def get_match_at_index(self, index: int) -> PouleMatch:
        """
        Gets a poule match at a specified index.
        
        Parameters
        ----------
        index : int
            The index to retrieve the poule match at.

        Returns
        -------
        PouleMatch
            The poule match at the index.

        Raises
        ------
        TypeError
            If the index is not an integer.
        ValueError
            If the list of matches is None or if the index is less than zero or greater than the index of the final match.
        """
        if self.matches is None:
            raise ValueError(f'Cannot get a poule match when the list of matches is None in poule {self.id}')

        validation.validate_int_in_range(index, 0, self.number_matches - 1, 'index', 'Poule', 'get_match_at_index')

        return self.matches[index]

    def get_current_match(self) -> PouleMatch:
        """Returns the current poule match."""
        return self.get_match_at_index(self.current_match_index)
    
    def get_next_match(self) -> PouleMatch | None:
        """Returns the match on deck or returns None if the current match is the last match."""
        if self.current_match_index == self.number_matches - 1:
            return None
        
        return self.get_match_at_index(self.current_match_index + 1)


    # --- Modification Methods ---
    def add_entry(self, entry: TournamentEntry) -> None:
        """
        Adds a valid entry to the poule and regenerates the poule matches after the addition.
        
        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add to the poule.

        Raises
        ------
        TypeError
            If the input entry is not a TournamentEntry
        ValueError
            If the input entry is already in the poule.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry - got {type(entry)}')
        if entry in self.entries:
            raise ValueError(f'Entry {entry.id} is already in poule {self.id}')
        
        # Add to list of entries
        self.entries.append(entry)

        # Regenerate matches
        self._generate_own_matches()

    def remove_entry(self, entry: TournamentEntry) -> None:
        """
        Removes a specified entry from the poule and regenerates the poule matches after the removal.
        
        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to remove from the poule.

        Raises
        ------
        TypeError
            If the input entry is not a TournamentEntry
        ValueError
            If the specified entry is not in the poule.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry - got {type(entry)}')
        if entry not in self.entries:
            raise ValueError(f'Entry {entry.id} is not in poule {self.id}')

        # Remove from list of entries
        self.entries.remove(entry)

        # Regenerate matches
        self._generate_own_matches()


    # --- Score Recording Methods ---
    def record_match_result(self, index: int, score1: int, score2: int) -> None:
        """
        Records the score of a specific match in the poule using the provided index.

        Parameters
        ----------
        index : int
            The index of the match to record the score at.
        score1 : int
            Entry 1's score.
        score2 : int
            Entry 2's score.
        """
        self.get_match_at_index(index).record_score(score1, score2)

    def record_current_match_result(self, score1: int, score2: int) -> None:
        """
        Records the score of the current match or returns None if there is no current match.
        
        Parameters
        ----------
        scoer1 : int
            Entry 1's score.
        score2 : int
            Entry 2's score.
        """
        # Record match result and move to the next match
        self.get_current_match().record_score(score1, score2)
        self.current_match_index += 1


    # --- Result Query Methods ---
    def calculate_results(self) -> SinglePouleResults:
        """Based on the current match results in the Poule, a PouleResult is calculated and returned."""
        if self.matches is None:
            raise ValueError(f'Cannot calculate results because no matches have been generated yet for this poule')

        # Create a list of empty poule results for each entry
        list_of_results = []
        for entry in self.entries:
            list_of_results.append(EntryPouleResult(entry, self.id))

        # Create the return object
        ret = SinglePouleResults(self.id, list_of_results)

        # Go through each match and update the results for the entries in the return value
        for match in self.matches:
            # Skip incomplete matches
            if not match.is_complete():
                continue

            # Extract match information
            entry1 = match.entry1
            entry2 = match.entry2
            winner = match.winner()

            # Update results for both entries in the match
            for entry in [entry1, entry2]:
                for result in ret.results:
                    if result.entry == entry:
                        result.matches += 1
                        if entry == winner:
                            result.victories += 1
                        if entry == entry1:
                            result.touches_scored += match.score1
                            result.touches_received += match.score2
                        else:
                            result.touches_scored += match.score2
                            result.touches_received += match.score1
                        break
        return ret

    # --- Helper Methods ---
    def _validate_entries_list(self, entries: list[TournamentEntry]):
        """
        Validates a given list of tournament entries.
        
        Parameters
        ----------
        entries : list[TournamentEntry]
            A list of TournamentEntry objects to be validated.

        Raises
        ------
        TypeError
            If entries is not a list or if any of the entries in the list is not a TournamentEntry object.
        ValueError
            If the number of entries is less than two.
        """
        if not isinstance(entries, list):
            raise TypeError(f'The entries variable must be of type list - got {type(entries)}')
        
        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'All entries must of type TournamentEntry - got entry {i} in list as type {type(entry)}')
                
        if len(entries) < 2:
            raise ValueError(f'There must be at least two entries in a poule - got {len(entries)}')
            
    def _validate_own_entries_list(self):
        """Validates the poule's own list of entries."""
        self._validate_entries_list(self.entries)

    def _create_match(self, id: int, index: int, match_pair: tuple[int, int]) -> PouleMatch:
        """
        Creates a poule match based on the given pair of fencer numbers.

        Parameters
        ----------
        id : int
            The unique identifier to give the match.
        index : int
            The index of the match in the list of poule matches.
        match_pair : tuple[int, int]
            A pair of numbers (i, j) such that entry 1 is fencer i in the poule and entry 2 is fencer j.

        Returns
        -------
        PouleMatch
            A poule match based on the specified input parameters.

        Raises
        ------
        TypeError
            If any of the id, index, or fencer numbers is not an integer, or if the match pair is not a tuple.
        ValueError
            If the index is out of the poule matches bounds, if the fencer numbers are out of the number of fencers bounds, 
            or if the id is not positive.
        """
        validation.validate_int_in_range(index, 0, self.number_matches - 1, 'index', 'Poule', '_create_match')

        # Validate the match pair tuple
        if not isinstance(match_pair, tuple):
            raise TypeError(f'Match pair must be a tuple - got {type(match_pair)}')
        
        if len(match_pair) != 2:
            raise ValueError(f'Match pair must be of length 2 - got {len(match_pair)}')
        
        # Validate the fencer numbers in the tuple
        fencer1_number = match_pair[0]
        fencer2_number = match_pair[1]

        validation.validate_int_in_range(fencer1_number, 1, self.size, 'fencer number 1', 'Poule', '_create_match')
        validation.validate_int_in_range(fencer2_number, 1, self.size, 'fencer number 2', 'Poule', '_create_match')

        # Get entries to create match with from poule entries list
        entry1 = self.entries[fencer1_number - 1]
        entry2 = self.entries[fencer2_number - 1]
        
        # Create and return poule match
        return PouleMatch(id=id, tournament_id=self.tournament_id, entry1=entry1, entry2=entry2, poule_id=self.id, match_index=index)
        
    def _generate_matches(self) -> list[PouleMatch]:
        """A helper method to genereate poule matches based on standard bout ordering and the current list of entries and standard bout ordering."""
        min_size, max_size = min(POULE_BOUT_ORDER.keys()), max(POULE_BOUT_ORDER.keys())
        
        if self.size < min_size or self.size > max_size:
            raise RuntimeError(f'Poule {self.id} has a size of {self.size}, which is outside the range of sizes that there are bout orders for \u2192 {min_size}-{max_size}.')
        
        # Get match order based on poule size
        match_order = POULE_BOUT_ORDER[self.size]

        # Set the list of poule matches
        return [self._create_match(index+1, index, match_pair) for index, match_pair in enumerate(match_order)]

    def _generate_own_matches(self) -> None:
        """A helper method to generate this poules list of matches."""
        # Clear any already existing matches
        if self.matches is not None:
            self.matches.clear()
            self.matches = None

        # Generate and assign the list of poule matches
        self.matches = self._generate_matches()