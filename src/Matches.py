from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod # ABC = "Abstract Base Class"
from TournamentEntry import TournamentEntry

# Parent Class
@dataclass
class Match(ABC):
    # Attributes
    id: int
    tournament_id: int
    score_to_win: int
    fencer1_entry: Optional[TournamentEntry] = None
    fencer2_entry: Optional[TournamentEntry] = None
    score1: int = 0
    score2: int = 0
    winner_entry: Optional[TournamentEntry] = None
    completed: bool = False

    @abstractmethod
    def match_type(self) -> str:
        pass

    # Methods
    def _validate_scores(self, score1: int, score2: int) -> bool:
        """ A helper function to validate two input scores. """
        return (type(score1) == int and
                type(score2) == int and
                score1 >= 0 and score1 <= self.score_to_win and
                score2 >= 0 and score2 <= self.score_to_win and
                score1 != score2)

    
    def record_score(self, score1: int, score2: int) -> bool:
        """ Record the result of a match by providing two scores: one for fencer 1 and one for fencer 2. """
        # Check if scores are valid
        if self._validate_scores(score1, score2):      
            # Update score values
            self.score1 = score1
            self.score2 = score2
            # Set winner
            if self.score1 > self.score2:
                return self.set_winner(self.fencer1_entry)
            else:
                return self.set_winner(self.fencer2_entry)
        return False
    
    def is_complete(self) -> bool:
        """ Checks whether a match is complete or not. """
        return self.completed
    
    def mark_complete(self) -> bool:
        """ Marks a match as complete and returns true; returns false if there was no need to mark it. """
        if self.is_complete():
            return False
        self.completed = True
        return True
    
    def set_winner(self, winner_entry: TournamentEntry) -> bool:
        """ Sets the winner of the match """
        if not isinstance(winner_entry, TournamentEntry):
            return False
        
        valid_entries = []

        if self.fencer1_entry is not None:
            valid_entries.append(self.fencer1_entry.id)

        if self.fencer2_entry is not None:
            valid_entries.append(self.fencer2_entry.id)

        if winner_entry.id not in valid_entries:
            return False
        
        self.winner_entry = winner_entry
        self.mark_complete()
        return True
    
    def get_winner(self) -> Optional[TournamentEntry]:
        """ Returns the winner of the match; None otherwise. """
        if self.is_complete():
            return self.winner_entry
        return None
    
    def get_loser(self) -> Optional[TournamentEntry]:
        """ Returns the loser of the match; None otherwise. """
        if self.is_complete() and self.fencer1_entry is not None and self.fencer2_entry is not None:
            if self.fencer1_entry.id != self.winner_entry.id:
                return self.fencer1_entry
            else:
                return self.fencer2_entry
        return None
    
# Subclasses
@dataclass
class PouleMatch(Match):
    # Attributes
    score_to_win: int = 5
    poule_id: Optional[int] = None
    bout_number: Optional[int] = None
    fencer1_number: Optional[int] = None
    fencer2_number: Optional[int] = None

    def __post_init__(self):
        if self.fencer1_entry is None or self.fencer2_entry is None:
            raise ValueError("PouleMatch requires two fencers.")

    # Methods
    def match_type(self) -> str:
        return "poule"

    def __str__(self):
        if (self.completed):
            return f'Poule Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (Finished)'
        return f'Poule Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (In-Progress)'


@dataclass
class DEMatch(Match):
    # Attributes
    fencer1_entry: TournamentEntry = None
    fencer2_entry: TournamentEntry = None
    score_to_win: int = 15
    round_number: int = 0 # Represents the round a DE match is in
    position: int = 0 # Index of this match within the round
    next_match_position: int = 0 # = position // 2

    # Methods
    def match_type(self) -> str:
        return "DE"
    
    def __str__(self):
        if self.fencer2_entry is None:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} : BYE'
        elif self.fencer1_entry is None:
            return f'DE Match - BYE : {self.fencer2_entry.fencer.display_name}'
        elif self.completed:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (Finished)'
        else:
            return f'DE Match - {self.fencer1_entry.fencer.display_name} {self.score1} : {self.score2} {self.fencer2_entry.fencer.display_name} (In-Progress)'