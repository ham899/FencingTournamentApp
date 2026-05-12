from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod # ABC = "Abstract Base Class"
from tournament_entry import TournamentEntry

# Parent Class
@dataclass
class Match(ABC):
    """
    Represents a match between two fencers in a tournament. It is an abstract class that acts as a parent for poule and DE match classes.
    A match is meant to either be initialized as an empty match, with none, one, or two fencers, then its scores recorded later or the match 
    and its results can be recorded upon the creation of a mtch using the constructor.
    """
    id: int
    tournament_id: int
    score_to_win: int
    entry1: Optional[TournamentEntry] = None
    entry2: Optional[TournamentEntry] = None
    score1: int = 0
    score2: int = 0
    winner_entry: Optional[TournamentEntry] = None
    completed: bool = False

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
        
        if type(self.score1) is not int:
            raise TypeError("Score 1 must be an integer.")
        
        if type(self.score2) is not int:
            raise TypeError("Score 2 must be an integer.")
        
        if self.winner_entry is not None and not isinstance(self.winner_entry, TournamentEntry):
            raise TypeError("Winner entry must be of type TournamentEntry or None.")
        
        if type(self.completed) is not bool:
            raise TypeError("Completed must be a boolean.")
        
        # Validate input values
        if self.id < 1:
            raise ValueError("Match ID must be a positive integer.")
        
        if self.tournament_id < 1:
            raise ValueError("Tournament ID must be a positive integer.")
        
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")
        
        if self.score1 < 0 or self.score1 > self.score_to_win or self.score2 < 0 or self.score2 > self.score_to_win:
            raise ValueError(f"Input score must be between 0 and {self.score_to_win}.")

        # Cannot input scores if there is a None entry
        if (self.entry1 is None or self.entry2 is None) and (self.score1 != 0 or self.score2 != 0):
            raise ValueError("Cannot input non-zero scores for matches without two entries present. Both scores must be 0 if there is at least one None entry.")

        # Validate winner entry
        if self.winner_entry is not None:
            valid_entries = []
            if self.entry1 is not None:
                valid_entries.append(self.entry1)
            if self.entry2 is not None:
                valid_entries.append(self.entry2)
            if self.winner_entry not in valid_entries:
                raise ValueError("Winner entry must be one of the fencers in the match.")
            # Set the match as complete if there is a winner entry
            self.completed = True

        # Do not allow a winner to be set if the scores are equal
        if self.score1 == self.score2 and self.winner_entry is not None:
            raise ValueError('Cannot set a winner entry if scores are equal')
        if self.score1 == self.score2 and self.completed==True:
            raise ValueError('Cannot set a match to be complete if the scores are equal')
        
        # Ensure that the scores reflect the winner entry provided
        if self.winner_entry is not None:
            if self.winner_entry == self.entry1 and self.score1 < self.score2:
                raise ValueError('Score inputted must reflect the winner entry provided')
            if self.winner_entry == self.entry2 and self.score1 > self.score2:
                raise ValueError('Score inputted must reflect the winner entry provided')

        ### All validity checks passed

        # Auto mark complete if winner entry is provided
        if (self.score1 > 0 or self.score2 > 0) and (self.winner_entry in [self.entry1, self.entry2]):
            self.completed = True
        # Derive winner entry from match score if marked complete
        if (self.score1 > 0 or self.score2 > 0) and (self.completed==True):
            if self.score1 > self.score2:
                self.winner_entry = self.entry1
            else:
                self.winner_entry = self.entry2
        # Derive winner entry and completion if one of the scores is the score to win
        if self.score1==self.score_to_win:
            self.winner_entry=self.entry1
            self.completed=True
        elif self.score2==self.score_to_win:
            self.winner_entry=self.entry2
            self.completed=True

        # Derive match winners in case of instances of BYEs
        if self.entry1 is not None and self.entry2 is None:
            self.winner_entry=self.entry1
            self.completed=True
        elif self.entry1 is None and self.entry2 is not None:
            self.winner_entry=self.entry2
            self.completed=True

    @abstractmethod
    def match_type(self) -> str:
        """ Returns the type of match as a string. """
        pass

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
            self.winner_entry = self.entry1
        else:
            self.winner_entry = self.entry2
        self.mark_complete()
    
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
        self.winner_entry = winner_entry
        self.mark_complete()
    
    def get_winner(self) -> Optional[TournamentEntry]:
        """ Returns the winner of the match; otherwise, returns None. """
        if self.is_complete():
            return self.winner_entry
        return None
    
    def get_loser(self) -> Optional[TournamentEntry]:
        """ Returns the loser of the match; otherwise returns None. """
        if self.is_complete() and self.winner_entry is None:
            raise ValueError('Cannot get loser entry. An error occurred: the winner entry should not be None if the match is complete.')
        
        if not self.is_complete():
            return None

        # If one entry is None, this could represent a BYE where there is a winner but no loser, so return None in this case
        if self.entry1 is None or self.entry2 is None:
            return None
        # Otherwise, both entries are present and return the loser
        else:
            return self.entry1 if self.winner_entry != self.entry1 else self.entry2
    
# Subclasses
@dataclass
class PouleMatch(Match):
    """
    Represents a poule match between two fencers in a tournament. Both fencers must be present for a valid poule match. 
    By convention, fencer 1 represents the fencer on the left of the referee and fencer 2 represents the fencer on the right.
    """
    poule_id: Optional[int] = None
    score_to_win: int = 5

    def __post_init__(self):
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if self.poule_id is not None and type(self.poule_id) is not int:
            raise TypeError("Poule ID must be None or an integer.")

        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        # Validate input values
        if self.poule_id is not None and self.poule_id < 1:
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


@dataclass
class DEMatch(Match):
    """
    Represents a DE match between two fencers in a tournament. To initialize a match, a fencer does not have to be present.
    Fencer 1 represents the fencer on the top bracket of a match in the tableau and fencer 2 represents the fencer on the bottom bracket of a match in the tableau.
    """
    # Fencers can be defaulted to None for matches with BYEs and empty matches in the tableau.
    fencer1_entry: TournamentEntry = None
    fencer2_entry: TournamentEntry = None
    score_to_win: int = 15
    round_index: Optional[int] = None # 0-indexed
    match_index: Optional[int] = None # 0-indexed within each round # = match_index // 2 in the next round of the bracket

    def __post_init__(self):
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if self.fencer1_entry is not None and not isinstance(self.fencer1_entry, TournamentEntry):
            raise TypeError("Fencer 1 entry must be of type TournamentEntry or None.")
        
        if self.fencer2_entry is not None and not isinstance(self.fencer2_entry, TournamentEntry):
            raise TypeError("Fencer 2 entry must be of type TournamentEntry or None.")
        
        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        if self.round_index is not None and type(self.round_index) is not int:
            raise TypeError("Round index must be an integer.")
        
        if self.match_index is not None and type(self.match_index) is not int:
            raise TypeError("Match index must be an integer.")
        
        # Validate input values
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")
        
        if self.round_index is not None and self.round_index < 0:
            raise ValueError("Round index must be a non-negative integer.")
        
        if self.match_index is not None and self.match_index < 0:
            raise ValueError("Match index must be a non-negative integer.")

    def match_type(self) -> str:
        """ Returns the type of match as a string. """
        return "DE"
    
    def __str__(self):
        if self.fencer1_entry is None and self.fencer2_entry is None:
            return f'DE Match - BYE : BYE'
        elif self.fencer2_entry is None:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} : BYE'
        elif self.fencer1_entry is None:
            return f'DE Match - BYE : {self.fencer2_entry.fencer.display_name}'
        elif self.completed:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (Finished)'
        else:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (In-Progress)'