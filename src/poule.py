from dataclasses import dataclass, field
from tournament_entry import TournamentEntry
from match import PouleMatch
from poule_orders import POULE_BOUT_ORDER
from poule_results import EntryPouleResult, PouleResult
from typing import Optional

@dataclass
class Poule:
    """ Represents a single poule in a tournament. """
    id: int
    tournament_id: int
    poule_number: int
    entries: list[TournamentEntry] # a sorted list such that index 0 --> fencer 1, etc.
    size: int = field(init=False) # Invariant: poule size must match the number of entries in the poule
    matches: list[PouleMatch] = field(default=None, init=False) # Invariant: matches should reflect the current entries in the poule
    current_match_index: int = field(default=0, init=False)

    def __post_init__(self):
        # Validate types
        if type(self.id) is not int:
            raise TypeError(f'Poule ID must be an integer')
        if type(self.tournament_id) is not int:
            raise TypeError(f'Tournament ID must be an integer')
        if type(self.poule_number) is not int:
            raise TypeError(f'Poule number must be an integer')
        if not isinstance(self.entries, list):
            raise TypeError(f'Entries must be a list')
        for entry in self.entries:
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'All entries must be of type TournamentEntry')        

        # Make a copy of the entries list
        self.entries = list(self.entries)

        # Validate values
        if self.id < 1:
            raise ValueError(f'Poule ID must be a positive integer')
        if self.tournament_id < 1:
            raise ValueError(f'Tournament ID must be a positive integer')
        if self.poule_number < 1:
            raise ValueError(f'Poule number must be a positive integer')

        # Set poule size
        self.size = len(self.entries)
        
        # Validate poule size
        if self.size < 2:
            raise ValueError(f'Poule size must be at least 2')

        # Generate the matches
        self.generate_matches()
    
    def number_of_matches(self) -> int:
        """Calculates the number of matches in the poule."""
        n = self.size
        return n*(n-1)//2

    def _create_match(self, match_number: int, match_pair: tuple[int,int]) -> PouleMatch:
        """Based on the poule fencer numbers provided, a PouleMatch is created."""
        if type(match_number) is not int:
            raise TypeError(f'Match number must be an integer')
        if not isinstance(match_pair, tuple):
            raise TypeError(f'Match pair must be a tuple')
        if match_number < 1 or match_number > self.number_of_matches():
            raise ValueError(f'Match number must be within the range of matches')
        if len(match_pair) != 2:
            raise ValueError(f'Match pair must be of length 2')
        if match_pair[0] < 1 or match_pair[0] > self.size:
            raise ValueError(f'Match pair fencer numbers must be between 1 and poule size')
        if match_pair[1] < 1 or match_pair[1] > self.size:
            raise ValueError(f'Match pair fencer numbers must be between 1 and poule size')
        
        # Create and return poule match
        return PouleMatch(id=match_number, tournament_id=self.tournament_id, entry1=self.entries[match_pair[0]-1], entry2=self.entries[match_pair[1]-1], poule_id=self.id)

    def add_entry(self, entry: TournamentEntry) -> None:
        """Adds a valid entry to the entries in this poule."""
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry')
        if entry in self.entries:
            raise ValueError(f'Entry is already in the poule')
        
        # Add to list of entries
        self.entries.append(entry)
        self.size += 1

        # Regenerate matches based on current entries
        self.generate_matches()

    def remove_entry(self, entry: TournamentEntry) -> None:
        """Removes an entry from the poule."""
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be of type TournamentEntry')
        if entry not in self.entries:
            raise ValueError(f'Entry is not in the poule')
        
        # Remove from list of entries
        self.entries.remove(entry)
        self.size -= 1

        # Regenerate matches based on current entries
        self.generate_matches()

    def generate_matches(self) -> None:
        """Based on the current list of entries and the standard bout orders, a match order is generated."""
        # Add matches based on match order
        bout_order = POULE_BOUT_ORDER[self.size]

        # Clear any already existing matches
        if self.matches is not None:
            self.matches.clear()

        # Set the list of poule matches
        self.matches = [Poule._create_match(self, match_number, bout_pair) for match_number, bout_pair in enumerate(bout_order, start=1)]
    
    def get_current_match(self) -> Optional[PouleMatch]:
        """Returns the current poule match or returns None if there is no current match."""
        if self.matches is None or self.current_match_index >= self.number_of_matches():
            return None
        return self.matches[self.current_match_index]

    def get_next_match(self) -> Optional[PouleMatch]:
        """Returns the match on deck or returns None if there is no match on deck."""      
        if self.matches is None or self.get_current_match() is None or self.current_match_index == self.number_of_matches()-1:
            return None
        return self.matches[self.current_match_index+1]
    
    def record_match_result(self, match_index: int, score1: int, score2: int) -> None:
        """Records the score of a specific match in the poule using the provided match index."""
        if self.matches is None:
            raise ValueError(f'Cannot record the match because no matches have been generated yet for this poule')
        if type(match_index) is not int:
            raise TypeError(f'Match index must be an integer')
        if match_index < 0 or match_index > self.number_of_matches()-1:
            raise ValueError(f'Match index must be within range')
        if type(score1) is not int or type(score2) is not int:
            raise TypeError(f'Scores must be integers')
        if score1 < 0 or score2 < 0:
            raise ValueError(f'Scores must be non-negative integers')

        # Record match result
        self.matches[match_index].record_score(score1, score2)

    def record_current_match_result(self, score1: int, score2: int) -> None:
        """Records the score of the current match or returns None if there is no current match."""
        if self.get_current_match() is None:
            raise ValueError(f'Cannot record the current match because there is no current match to record')

        # Record match result and move to the next match
        self.record_match_result(self.current_match_index, score1, score2)
        self.current_match_index += 1

    def is_complete(self) -> bool:
        """Checks if the poule is complete."""
        if self.matches is None:
            return False
        return all(match.is_complete() for match in self.matches)
        
    def calculate_results(self) -> PouleResult:
        """Based on the current match results in the Poule, a Poule result is calculated."""
        if self.matches is None:
            raise ValueError(f'Cannot calculate results because no matches have been generated yet for this poule')

        # Create a list of empty poule results for each entry
        list_of_results = []
        for entry in self.entries:
            list_of_results.append(EntryPouleResult(entry, self.id))

        # Create the return object
        ret = PouleResult(self.id, list_of_results)

        # Go through each match and update the results for the entries in the return value
        for match in self.matches:
            # Skip incomplete matches
            if not match.is_complete():
                continue

            # Extract match information
            entry1 = match.entry1
            entry2 = match.entry2
            winner = match.winner

            # Update results for both entries in the match
            for entry in [entry1, entry2]:
                for result in ret.results:
                    if result.entry == entry:
                        result.matches_fenced += 1
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

    # Print Methods
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

    def __str__(self):
        ret = f'Poule {self.poule_number} of size {self.size} with Entrants: '
        i = 0
        while i < self.size:
            if (i < self.size-1):
                ret += f'{self.entries[i].fencer.display_name}, '
            else:
                ret += f'{self.entries[i].fencer.display_name}'
            i+=1
        return ret