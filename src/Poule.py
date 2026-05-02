from dataclasses import dataclass
from TournamentEntry import TournamentEntry
from Matches import PouleMatch
from poule_orders import POULE_BOUT_ORDER
from PouleResults import PouleResult, PouleResults
from typing import Optional

@dataclass
class Poule:
    # Attributes
    id: int
    tournament_id: int
    poule_number: int
    poule_size: int
    entries: list[TournamentEntry] # a sorted list such that index 0 --> fencer 1, etc.
    matches: Optional[list[PouleMatch]] = None
    current_match_index: int = 0

    # Generate the matches after entrants are added
    def __post_init__(self):
        self.matches = self.generate_matches()

    # Helper Methods
    @staticmethod
    def _is_positive_integer(value: int) -> bool:
        """Returns true if the input is a positive integer; false otherwise."""
        return type(value) is int and value > 0

    @staticmethod
    def _validate_id(id: int) -> bool:
        """Returns true if the input ID is valid; false otherwise."""
        return Poule._is_positive_integer(id)

    @staticmethod
    def _validate_poule_number(poule_number: int) -> bool:
        """Returns true if the input number is a valid poule number; false otherwise."""
        return Poule._is_positive_integer(poule_number)
    
    def _create_match(self, match_pair: tuple[int,int]) -> PouleMatch:
        """Based on the poule IDs provided, a PouleMatch is created."""
        poule_fencer_1_entry = self.entries[match_pair[0]-1]
        poule_fencer_2_entry = self.entries[match_pair[1]-1]
        return PouleMatch(1, self.tournament_id, poule_fencer_1_entry, poule_fencer_2_entry)

    # Methods
    def add_entry(self, entry: TournamentEntry) -> bool:
        """Adds a valid entry to the entries in this poule."""
        # Validate Entry
        if not isinstance(entry, TournamentEntry):
            return False
        # Add to list of entries
        self.entries.append(entry)
        return True

    def generate_matches(self) -> list[PouleMatch]:
        """Based on the current list of entries and the standard bout orders, a match order is generated."""
        # Add matches based on match order
        bout_order = POULE_BOUT_ORDER[self.poule_size]

        # Clear any already existing matches
        if self.matches is not None:
            self.matches.clear()

        # Make and return a list of poule matches
        return [Poule._create_match(self, bout_pair) for bout_pair in bout_order]
    
    def number_of_matches(self):
        """Calculates the number of matches in the poule."""
        p = self.poule_size
        return p*(p-1)//2
        
    def get_current_match(self) -> PouleMatch:
        """Gets the current poule match."""
        if self.matches is None or self.current_match_index >= self.number_of_matches():
            return None
        return self.matches[self.current_match_index]

    def get_next_match(self) -> PouleMatch:
        """Gets the match on deck."""      
        if self.matches is None or self.get_current_match() is None or self.current_match_index == self.number_of_matches()-1:
            return None
        return self.matches[self.current_match_index+1]
    
    def record_current_match_result(self, score1: int, score2: int) -> PouleMatch:
        """Records the score of the current match."""
        if self.matches is None or self.get_current_match() is None:
            return None
        current_match = self.get_current_match()
        current_match.record_score(score1, score2)
        self.current_match_index += 1
        return current_match

    def is_complete(self) -> bool:
        """Checks if the poule is complete."""
        if self.matches is None:
            return False
        return all(match.is_complete() for match in self.matches)
        
    def calculate_results(self) -> PouleResults:
        """Based on the current match results in the Poule, a Poule result is calculated."""
        i = 0
        dict_of_results = dict()
        while i < self.poule_size:
            dict_of_results[self.entries[i].id] = PouleResult(self.entries[i], self.id)
            i+=1
        
        ret = PouleResults(self.id, dict_of_results)

        for match in self.matches:
            # Skip incomplete matches
            if not match.is_complete():
                continue

            entry1 = match.fencer1_entry
            entry2 = match.fencer2_entry
            winner = match.winner_entry

            for entry in [entry1, entry2]:
                ret.results[entry.id].matches_fenced += 1
                if (entry.id == winner.id):
                    ret.results[entry.id].victories += 1
                if (entry.id == entry1.id):
                    ret.results[entry.id].touches_scored += match.score1
                    ret.results[entry.id].touches_received += match.score2
                else:
                    ret.results[entry.id].touches_scored += match.score2
                    ret.results[entry.id].touches_received += match.score1
                    
        return ret

    # Print Methods
    def __str__(self):
        ret = f'Poule {self.poule_number} of size {self.poule_size} with Entrants: '
        i = 0
        while i < self.poule_size:
            if (i < self.poule_size-1):
                ret += f'{self.entries[i].fencer.display_name}, '
            else:
                ret += f'{self.entries[i].fencer.display_name}'
            i+=1
        return ret
    
    def print_matches(self) -> None:
        """Prints out all the matches in the poule - the completed and incomplete ones."""
        if self.matches is not None:
            for match in self.matches:
                print(match)

    def print_remaining_matches(self) -> None:
        """Prints out the matches still to be finished in the poule."""
        if self.matches is not None:
            for match in self.matches[self.current_match_index:]:
                print(match)
