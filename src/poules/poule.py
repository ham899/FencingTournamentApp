from dataclasses import dataclass, field

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule_results import SinglePouleResults
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
    matches : list[PouleMatch], default=list, init=False
        The matches and the order that they are to be done in for the poule. 
        **Invariant:** they must always reflect the current list of entries in the poule.
    """
    id: int
    tournament_id: int
    poule_number: int
    entries: list[TournamentEntry]
    matches: list[PouleMatch] = field(default_factory=list, init=False) # Invariant: matches should reflect the current entries in the poule


    # --- Initialization and Validation Methods ---
    def __post_init__(self):
        """Validates the attributes of the poule and generates the poule matches based on the current list of entries."""
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
    def has_started(self) -> bool:
        """Checks if the poule has started."""
        if self.matches is None:
            return False
        return any(match.is_complete() for match in self.matches)

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


    def get_current_match(self) -> PouleMatch | None:
        """Returns the current poule match."""
        # Get the next incomplete match in the series of incomplete matches or return None if all matches are complete
        return next((match for match in self.matches if match.is_incomplete()), None)


    def get_next_match(self) -> PouleMatch | None:
        """Returns the match on deck or returns None if the current match is the last match."""
        current_match = self.get_current_match()

        # Case: All matches are complete
        if current_match is None:
            return None

        # Find next incomplete match after current match
        current_match_index = current_match.match_index
        for match in self.matches[current_match_index + 1:]:
            if match.is_incomplete():
                return match
        
        # If the current match is the last match
        return None


    # --- Entry Modification Methods ---
    def add_entry(self, entry: TournamentEntry) -> None:
        """
        Adds a valid entry to the poule and regenerates the poule's bout order while preserving the results of the matches that already occurred.
        
        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add to the poule.

        Raises
        ------
        TypeError
            If the input entry is not a TournamentEntry
        ValueError
            If the input entry is already in the poule, belongs to another
            tournament, or would create an unsupported poule size.

        RuntimeError
            If a match in the poule is currently in progress.
        """
        self._validate_entry(entry)
        
        if entry in self.entries:
            raise ValueError(f'Entry {entry.id} is already in poule {self.id}')

        # Reject adding an entry during an in-progress bout
        if any(match.is_in_progress() for match in self.matches):
            raise RuntimeError(f'Cannot add an entry while a match is in progress in poule {self.id}.')

        # Validate that adding the entry will be valid
        proposed_entries = self.entries + [entry]
        self._validate_entries_list(proposed_entries)
        self._validate_poule_size(len(proposed_entries))

        # Generate new matches to potentially add to matches attribute
        new_matches = self._generate_matches(proposed_entries)

        # Transfer results of any already completed matches to new matches
        self._transfer_results(self.matches, new_matches)

        # If all steps were successful, update the poule attributes
        self.entries = proposed_entries
        self.matches = new_matches


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
            If the specified entry is not in the poule, or if the poule has already started.
        """
        if self.has_started():
            raise ValueError(f'Cannot remove entry from poule {self.id} because the poule has already started')

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
        match = self.get_match_at_index(index)
        match.record_score(score1, score2)


    def record_current_match_result(self, score1: int, score2: int) -> None:
        """
        Records the score of the current match or returns None if there is no current match.
        
        Parameters
        ----------
        score1 : int
            Entry 1's score.
        score2 : int
            Entry 2's score.
        """
        match = self.get_current_match()
        
        if match is None:
            raise RuntimeError(f'Poule {self.id} is already complete.')

        match.record_score(score1, score2)


    # --- Result Query Methods ---
    def calculate_results(self) -> SinglePouleResults:
        """Calculates a SinglePouleResults object based on the current match results in the Poule."""
        if self.matches is None:
            raise ValueError(f'Cannot calculate results because no matches have been generated yet for poule {self.id}')

        # Initialize a new SinglePouleResults object where result data is initialized to zero for each entry in the poule
        poule_results = SinglePouleResults(self.id, self.entries)

        # Add each match's result to the SinglePouleResults container
        for match in self.matches:
            # Skip incomplete matches
            if not match.is_complete():
                continue

            poule_results.add_match_result(match)

        # Return the filled in SinglePouleResults object
        return poule_results


    # --- Helper Methods ---
    def _validate_poule_size(self, size: int) -> None:
        """Validates that a poule size is supported by a valid bout order."""
        supported_sizes = list(POULE_BOUT_ORDER.keys())
        supported_sizes.sort()

        if size not in supported_sizes:
            raise ValueError(f'Cannot create a poule with {size} entries because no bout order exists for it; the supported sizes are {supported_sizes[0]}-{supported_sizes[-1]}.')


    def _validate_entry(self, entry: TournamentEntry) -> None:
        """Validates that a tournament entry is valid for this poule."""
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be a tournament entry - got {type(entry)}')
        
        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry {entry.id} must belong to this tournament ({self.tournament_id}) - got {entry.tournament_id}')


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
                
            if entry.tournament_id != self.tournament_id:
                raise ValueError(f'All entries must have the same tournament ID as the poule - entry {i} has tournament ID {entry.tournament_id} when poule has tournament ID {self.tournament_id}')

            if entries.count(entry) != 1:
                raise ValueError(f'The entries must be unique; entry {entry.id} at index {i} is not unique and has a duplicate entry in the list in poule {self.id}')            

        if len(entries) < 2:
            raise ValueError(f'There must be at least two entries in a poule - got {len(entries)}')

        self._validate_poule_size(len(entries))


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
        validation.validate_positive_int(id, 'id', 'Poule', '_create_match')
        validation.validate_int_in_range(index, 0, self.number_matches - 1, 'index', 'Poule', '_create_match')

        # Validate the match pair tuple
        if not isinstance(match_pair, tuple):
            raise TypeError(f'Match pair must be a tuple - got {type(match_pair)}')
        
        if len(match_pair) != 2:
            raise ValueError(f'Match pair must be of length 2 - got {len(match_pair)}')
        
        # Validate the fencer numbers in the tuple
        fencer1_number = match_pair[0]
        fencer2_number = match_pair[1]

        if fencer1_number == fencer2_number:
            raise ValueError(f'Fencer numbers in match pair must be different - got {fencer1_number} and {fencer2_number}')

        validation.validate_int_in_range(fencer1_number, 1, self.size, 'fencer number 1', 'Poule', '_create_match')
        validation.validate_int_in_range(fencer2_number, 1, self.size, 'fencer number 2', 'Poule', '_create_match')

        # Get entries to create match with from poule entries list
        entry1 = self.entries[fencer1_number - 1]
        entry2 = self.entries[fencer2_number - 1]

        # Check that the entries are distinct
        if entry1 == entry2:
            raise ValueError(f'Entries in match pair must be different - got {entry1} and {entry2}')

        # Create and return poule match
        return PouleMatch(id=id, tournament_id=self.tournament_id, entry1=entry1, entry2=entry2, poule_id=self.id, match_index=index)


    def _generate_matches(self, entries: list[TournamentEntry]) -> list[PouleMatch]:
        """A helper method to genereate poule matches based on standard bout ordering and a provided list of entries."""
        min_size, max_size = min(list(POULE_BOUT_ORDER.keys())), max(list(POULE_BOUT_ORDER.keys()))
        
        if len(entries) < min_size or len(entries) > max_size:
            raise RuntimeError(f'This list of entries has size {len(entries)}, which is outside the range of sizes that there are bout orders for \u2192 {min_size}-{max_size}.')
        
        # Get match order based on poule size
        match_order = POULE_BOUT_ORDER[len(entries)]

        # Set the list of poule matches
        return [self._create_match(index+1, index, match_pair) for index, match_pair in enumerate(match_order)]


    def _generate_own_matches(self) -> None:
        """A helper method to generate this poule's list of matches and reset the current match index to 0."""
        self.matches = self._generate_matches(self.entries)


    def _transfer_results(self, source_matches, destination_matches) -> None:
        """Transfers any completed match results from the source matches to the destination matches."""
        # Validate inputs
        if not isinstance(source_matches, list):
            raise TypeError(f'Source matches in Poule._transfer_results() must be a list - got {type(source_matches)}.')
        
        for i, match in enumerate(source_matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'All source matches must be of type PouleMatch in Poule._transfer_results() - got {type(match)} at index {i}.')

        if not isinstance(destination_matches, list):
            raise TypeError(f'Destination matches in Poule._transfer_results() must be a list - got {type(destination_matches)}.')
        
        for i, match in enumerate(destination_matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'All destination matches must be of type PouleMatch in Poule._transfer_results() - got {type(match)} at index {i}.')
        
        # Get completed matches from source matches
        previous_results = [match for match in source_matches if match.is_complete()]

        # If no source matches were completed, do nothing
        if len(previous_results) == 0:
            return

        # Transfer results to destination matches
        for match_prev in previous_results:
            result_copied = False
            entries_prev = match_prev.entries()

            for match_new in destination_matches:                
                entries_new = match_new.entries()

                if entries_new == entries_prev:
                    if match_prev.is_forfeit():
                        forfeiting_index = match_prev.forfeited_index
                        match_new.forfeit(forfeiting_index)
                        result_copied = True
                        break
                    else:
                        match_new.record_score(match_prev.score1, match_prev.score2)
                        result_copied = True
                        break

                elif entries_new == entries_prev[::-1]:
                    if match_prev.is_forfeit():
                        forfeiting_index = match_prev.forfeited_index - 1
                        match_new.forfeit(forfeiting_index)
                        result_copied = True
                    else:
                        match_new.record_score( match_prev.score2, match_prev.score1)
                        result_copied = True
                        break

            if not result_copied:
                raise RuntimeError(f'Could not transfer the result of match {match_prev.id} to any match in the destination matches.')