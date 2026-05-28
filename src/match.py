from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod # ABC = "Abstract Base Class"
from tournament_entry import TournamentEntry

### Parent Class ###
@dataclass
class Match(ABC):
    """
    Represents a match between two fencers in a tournament. It is an abstract class that acts as a parent for poule and DE match classes.
    A match is meant to either be initialized as an empty match, with none, one, or two fencers and its scores are meant to be recorded later.
    """
    id: int
    tournament_id: int
    score_to_win: int
    entry1: TournamentEntry = field(default=None)
    entry2: TournamentEntry = field(default=None)
    score1: int = field(default=0, init=False)
    score2: int = field(default=0, init=False)
    winner: TournamentEntry = field(default=None, init=False)
    completed: bool = field(default=False, init=False)

    def __post_init__(self):
        # Validate input types
        if type(self.id) is not int:
            raise TypeError("Match ID must be an integer.")
        
        if type(self.tournament_id) is not int:
            raise TypeError("Tournament ID must be an integer.")
        
        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        if self.entry1 is not None and not isinstance(self.entry1, TournamentEntry):
            raise TypeError("Fencer 1 entry must be of type TournamentEntry or None.")
        
        if self.entry2 is not None and not isinstance(self.entry2, TournamentEntry):
            raise TypeError("Fencer 2 entry must be of type TournamentEntry or None.")
        
        # Validate input values
        if self.id < 1:
            raise ValueError("Match ID must be a positive integer.")
        
        if self.tournament_id < 1:
            raise ValueError("Tournament ID must be a positive integer.")
        
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")

    @abstractmethod
    def match_type(self) -> str:
        """ Returns the type of match as a string. """
        pass

    def is_complete(self) -> bool:
        """ Checks whether a match is complete or not. """
        return self.completed
    
    def mark_complete(self) -> None:
        """ Marks a match as complete. """
        self.completed = True
    
    def set_winner(self, winner_entry: TournamentEntry) -> None:
        """ Sets the winner of the match. """
        if not isinstance(winner_entry, TournamentEntry):
            raise TypeError('Winner entry must be of type TournamentEntry.')
        
        # Make a list of valid entries to check the winner entry against
        valid_entries = []
        if self.entry1 is not None:
            valid_entries.append(self.entry1)
        if self.entry2 is not None:
            valid_entries.append(self.entry2)
        if winner_entry not in valid_entries:
            raise ValueError('Winner entry must be one of the fencers in the match.')

        # Set the winner and mark the match as complete
        self.winner = winner_entry
        self.mark_complete()

    def get_winner(self) -> Optional[TournamentEntry]:
        """ Returns the winner of the match; otherwise, returns None. """
        if self.is_complete():
            return self.winner
        return None

    def get_loser(self) -> Optional[TournamentEntry]:
        """ Returns the loser of the match; otherwise returns None. """
        if self.is_complete() and self.winner is None:
            raise ValueError('Cannot get loser entry. The winner entry should not be None if the match is complete.')
        
        if not self.is_complete():
            return None

        # If one entry is None, this could represent a BYE where there is a winner but no loser, so return None in this case
        if self.entry1 is None or self.entry2 is None:
            return None
        # Otherwise, both entries are present and return the loser
        else:
            return self.entry1 if self.winner != self.entry1 else self.entry2

    def record_score(self, score1: int, score2: int) -> None:
        """ Record the result of a match by providing two scores: one for fencer 1 and one for fencer 2. """
        # Validate input scores
        if type(score1) is not int or type(score2) is not int:
            raise TypeError("Scores must be integers.")
        
        if score1 < 0 or score1 > self.score_to_win or score2 < 0 or score2 > self.score_to_win:
            raise ValueError(f"Scores must be between 0 and {self.score_to_win}.")

        if score1 == score2:
            raise ValueError('The input scores cannot be equal; matches cannot end in a tie.')

        # Update score values
        self.score1 = score1
        self.score2 = score2

        # Set winner
        if self.score1 > self.score2:
            self.set_winner(self.entry1)
        else:
            self.set_winner(self.entry2)
  
### Subclasses ###
@dataclass(kw_only=True)
class PouleMatch(Match):
    """
    Represents a poule match between two fencers in a tournament. Both fencers must be present for a valid poule match. 
    By convention, fencer 1 represents the fencer on the left of the referee and fencer 2 represents the fencer on the right.
    """
    poule_id: int
    score_to_win: int = 5

    def __post_init__(self):
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if self.poule_id is not None and type(self.poule_id) is not int:
            raise TypeError("Poule ID must be an integer.")

        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        # Validate input values
        if self.poule_id < 1:
            raise ValueError("Poule ID must be a positive integer.")

        # A poule match must be supplied with two valid fencer entries
        if self.entry1 is None or self.entry2 is None:
            raise ValueError("A poule match requires two fencers. There are no BYEs in poule matches.")

    def match_type(self) -> str:
        """ Returns the type of match as a string. """
        return "poule"

    def __str__(self):
        if self.completed:
            return f'Poule Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (Finished)'
        return f'Poule Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (In-Progress)'


@dataclass(kw_only=True)
class DEMatch(Match):
    """
    Represents a DE match between two fencers in a tournament. To initialize a match, a fencer does not have to be present.
    Fencer 1 represents the fencer on the top bracket of a match in the tableau and fencer 2 represents the fencer on the bottom bracket of a match in the tableau.
    """
    # Fencers can be defaulted to None for matches with BYEs and empty matches in the tableau.
    round_index: int # 0-indexed
    match_index: int # 0-indexed within each round # = match_index // 2 in the next round of the bracket
    score_to_win: int = 15
    
    def __post_init__(self):
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if self.entry1 is not None and not isinstance(self.entry1, TournamentEntry):
            raise TypeError("Fencer 1 entry must be of type TournamentEntry or None.")
        
        if self.entry2 is not None and not isinstance(self.entry2, TournamentEntry):
            raise TypeError("Fencer 2 entry must be of type TournamentEntry or None.")
        
        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        if type(self.round_index) is not int:
            raise TypeError("Round index must be an integer.")
        
        if type(self.match_index) is not int:
            raise TypeError("Match index must be an integer.")
        
        # Validate input values
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")
        
        if self.round_index < 0:
            raise ValueError("Round index must be a non-negative integer.")
        
        if self.match_index < 0:
            raise ValueError("Match index must be a non-negative integer.")
        
        # Derive winner if match is a BYE
        if self.entry1 is not None and self.entry2 is None:
            self.set_winner(self.entry1)
        elif self.entry1 is None and self.entry2 is not None:
            self.set_winner(self.entry2)

    def match_type(self) -> str:
        """ Returns the type of match as a string. """
        return "DE"
    
    def add_entry(self, entry: TournamentEntry, location: int) -> None:
        """ Adds an entry to the match at the given location (0 for entry 1 and 1 for entry 2) """
        if not isinstance(entry, TournamentEntry):
            raise TypeError('Entry must be a Tournament Entry object')
        if type(location) is not int:
            raise TypeError('Location must be an integer')
        if location not in [0,1]:
            raise ValueError('Location must be either 0 or 1')

        if location == 0:
            self.entry1 = entry
        else:
            self.entry2 = entry

    def add_entry1(self, entry: TournamentEntry) -> None:
        """ Adds an entry to the match as entry 1. """
        self.add_entry(entry, 0)

    def add_entry2(self, entry: TournamentEntry) -> None:
        """ Add an entry to the match as entry 2. """
        self.add_entry(entry, 1)

    def is_bye(self):
        """ Returns true if the match is a BYE; false otherwise. """
        if self.round_index != 0:
            return False
        if self.match_index % 2 == 0:
            if self.entry1 is not None and self.entry2 is None:
                return True
            else:
                return False
        else:
            if self.entry1 is None and self.entry2 is not None:
                return True
            else:
                return False
    
    def __str__(self):
        if self.entry1 is None and self.entry2 is None:
            return f'DE Match - BYE : BYE'
        elif self.entry2 is None:
            return f'DE Match - {self.entry1.fencer.display_name} : BYE'
        elif self.entry1 is None:
            return f'DE Match - BYE : {self.entry2.fencer.display_name}'
        elif self.completed:
            return f'DE Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (Finished)'
        else:
            return f'DE Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (In-Progress)'